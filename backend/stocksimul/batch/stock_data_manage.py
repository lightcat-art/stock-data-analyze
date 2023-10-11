from ..models import PriceInfo, InfoUpdateStatus, EventInfo, FundamentalInfo
from pykrx.website import krx
from pykrx import stock
from datetime import timedelta, datetime
from dateutil.relativedelta import relativedelta
from django.db import transaction
import time
import numpy as np
from numpy.lib import math
import logging
from ..config.stockConfig import BATCH_TEST_CODE_YN, BATCH_TEST_CODE_LIST, BATCH_FIRST_INSERT_ALL
from ..custom.opendartreader.dart_manager import DartManager
from ..custom.opendartreader.dart_config import DartConfig

'''
1. api 통신을 통해 현재 마켓에 등록된 종목정보를 모두 받아온다.
2. 테이블에 등록된 종목정보와 api에서 받아온 종목정보를 비교하여, 삭제된 종목, 추가된 종목, 현상유지 종목  구분을 해야함.
    1. 현재 등록된 종목/신규종목에 대해서는, 하루단위 주가를 받아와 업데이트할것임.
        1. 테이블에 등록이 되지 않은 종목의 경우 신규종목으로 간주.
        2. 신규 종목은 종목코드 정보도 같이 저장.
        3. 몇몇 종목은 삭제된 종목일수 있음.
            1. 삭제된 종목의 경우에는 주가정보와 종목정보를 삭제조치.
        4. 시가,종가,고가,저가 가 모두 0이면 휴일으로 간주하고 스킵.
3. 종목업데이트현황 등록은 제일 마지막에 실행
4. 며칠만에 앱을 재실행하는 경우에는 
신규종목이 있을 경우 daily_batch만 실행하면 updatestatus에 등록이 안되어있기 때문에 init_batch를 무조건 실행해줘야함.
 -> BATCH_FIRST_INSERT_ALL 플래그를 True로 해놓아야함.
ps. 
* 장 시작 전에는 시가,고가,종가,저가 가 모두 0으로 조회됨.
'''
first = False  # 첫 insert 진행중 여부

logger = logging.getLogger('batch')


# def stock_batch():
#     print('stock_batch start')
#     manage_event_all()

def validate_connection():
    try:
        event_info = EventInfo.objects.all()
        logger.info('[validate_connection] event_info count={}'.format(event_info.count()))
        # logger.info('[test_connection] event_info selected')
    except Exception as e:
        logger.exception('[validate_connection] error occured')


# def make_sure_mysql_usable():
#     from django.db import connection, connections
#     # mysql is lazily connected to in django.
#     # connection.connection is None means
#     # you have not connected to mysql before
#     if connection.connection and not connection.is_usable():
#         # destroy the default mysql connection
#         # after this line, when you use ORM methods
#         # django will reconnect to the default mysql
#         del connections._connections.default


def manage_event_init():
    try:
        logger.info('[manage_event_init] start')
        global first
        today_org = datetime.now()
        logger.info('cur time = {}'.format(today_org))
        today = today_org.strftime('%Y%m%d')

        cur_event_info = EventInfo.objects.all()
        start_date_str = datetime.now().strftime('%Y%m%d')
        market_event_info = krx.get_market_ticker_and_name(date=start_date_str, market='ALL')

        whole_code = [{'event_code': k, 'event_name': v} for k, v in market_event_info.iteritems()]
        # 전체 기간 전체 종목 insert
        if cur_event_info.count() == 0 or BATCH_FIRST_INSERT_ALL:
            logger.info('first batch start')
            first = True

            get_market_data_time_taken = 0.0
            insert_market_data_time_taken = 0.0
            insert_count = 0

            for item in whole_code:
                event_code = item['event_code']
                # 특정 코드 테스트 시 사용
                if BATCH_TEST_CODE_YN:
                    if event_code not in BATCH_TEST_CODE_LIST:
                        continue
                # 기존 등록된 종목인지 확인.
                event_info = EventInfo.objects.filter(event_code=event_code)
                if event_info.count() != 0:
                    event_status = InfoUpdateStatus.objects.filter(stock_event_id=event_info.first().stock_event_id)
                    if event_status.count() != 0:  # 이미 등록된 것이면 스킵.
                        logger.info('{} already inserted. skip inserting.'.format(item['event_code']))
                        continue
                    else:  # 종목정보 INSERT 중, 비정상종료된 케이스로 간주하고 해당 종목정보들 삭제 후 재등록
                        logger.info(
                            '{} already inserted. but not completed. delete and re-insert.'.format(item['event_code']))
                        event_price = PriceInfo.objects.filter(stock_event_id=event_info.first().stock_event_id)
                        event_info.delete()
                        event_price.delete()

                # 신규종목일 경우에는 위의 로직을 무시하고, 기존정보가 없으므로 그냥 INSERT 된다.
                insert_count += 1
                logger.info('{} inserting.. inserting count = {}'.format(item['event_code'], insert_count))
                # stockevent 테이블에 insert
                with transaction.atomic():
                    entry = EventInfo(**item)
                    entry.save()

                # print('event_code = ', event_code)
                event_info = EventInfo.objects.filter(event_code=event_code)
                start_get_market_data = datetime.now().timestamp()

                price_info_df = stock.get_market_ohlcv_by_date(fromdate='19000101', todate=today, ticker=event_code)
                price_info_df = price_info_df.replace({np.nan: None})
                # print('price_info = ', price_info_df)
                end_get_market_data = datetime.now().timestamp()
                get_market_data_time_taken += (end_get_market_data - start_get_market_data)

                price_info_df = price_info_df.reset_index()
                price_info_df.rename(
                    columns={'날짜': 'date', '시가': 'open', '종가': 'close', '거래량': 'volume', '고가': 'high', '저가': 'low',
                             '거래대금': 'value', '등락률': 'up_down_rate'},
                    inplace=True)
                # stockprice 테이블에 insert
                with transaction.atomic():
                    for price_item in price_info_df.to_dict('records'):
                        if price_item['open'] != 0 and price_item['high'] != 0 \
                                and price_item['low'] != 0 and price_item['close'] != 0:
                            entry = PriceInfo(**price_item)
                            entry.stock_event_id = event_info.first().stock_event_id
                            entry.save()

                end_insert_market_data = datetime.now().timestamp()
                insert_market_data_time_taken += (end_insert_market_data - end_get_market_data)

                status_dict = {'table_type': 'P', 'mod_dt': datetime.now(), 'reg_dt': datetime.now(),
                               'stock_event_id': event_info.first().stock_event_id}
                event_status_insert = InfoUpdateStatus(**status_dict)
                event_status_insert.save()

            logger.info('get market data time = {}'.format(get_market_data_time_taken))
            logger.info('insert market data time = {}'.format(insert_market_data_time_taken))
            logger.info('[manage_event_init] end')
        else:
            logger.info('[manage_event_init] skip.')
    except Exception as e:
        logger.exception('[manage_event_init] error occured')
    finally:
        first = False


def manage_event_daily():
    try:
        logger.info('[manage_event_daily] start')
        global first
        today_org = datetime.now()
        logger.debug('cur time = ' + str(today_org))
        today = today_org.strftime('%Y%m%d')

        cur_event_info = EventInfo.objects.all()
        start_date_str = datetime.now().strftime('%Y%m%d')
        market_event_info = krx.get_market_ticker_and_name(date=start_date_str, market='ALL')

        whole_code_df = [{'event_code': k, 'event_name': v} for k, v in market_event_info.iteritems()]
        # 하루단위 전체종목 insert
        if cur_event_info.count() != 0:
            logger.info('first_batch executing status = {}'.format(first))
            if not first:
                price_info_df = stock.get_market_ohlcv_by_ticker(date=today, market='ALL')
                # 전체종목에 대해 시가,종가,고가,저가 가 모두 0이면 휴일으로 간주하고 스킵.
                holiday = (price_info_df[['시가', '고가', '저가', '종가']] == 0).all(axis=None)
                # stockprice 테이블 업데이트 - 신규/기존 종목
                # price_info_df = price_info.reset_index() # 종목코드를 컬럼으로 빼기.
                price_info_df.rename(
                    columns={'티커': 'event_code', '시가': 'open', '종가': 'close', '거래량': 'volume', '고가': 'high',
                             '저가': 'low',
                             '거래대금': 'value', '등락률': 'up_down_rate'}, inplace=True)
                price_info_df['date'] = datetime.now()

                # if not holiday:
                new_event_result = {}
                del_event_result = []
                # delete 항목을 따로 나중에 제외시키기 위해 현재 등록되어있는 종목 미리 모두 다 넣어둠.
                for cur_event in cur_event_info:
                    del_event_result.append(cur_event.event_code)
                # 등록되어있는 종목, 신규종목, 삭제될 종목 구분.
                for market_event_code, market_event_name in market_event_info.iteritems():
                    code_exist = False
                    code_new = False
                    code_delete = False
                    for cur_event in cur_event_info:
                        if cur_event.event_code == market_event_code:
                            code_exist = True
                            # event_result['exist'].append(item['event_code'])
                            # 현재 시장에서 존재하는 종목이 db에서 존재한다면 그 외에는 모두 삭제될 종목이라는 점을 이용하여 필터링.
                            del_event_result.remove(market_event_code)

                    if not code_exist:
                        code_new = True
                        new_event_result.update({market_event_code: market_event_name})

                # 삭제 종목 관리
                del_event_id_list = []

                for delete_event_code in del_event_result:
                    with transaction.atomic():
                        del_event_info = EventInfo.objects.filter(event_code=delete_event_code)
                        if len(del_event_info) != 0:
                            logger.info('종목 삭제 : {} / {}'.format(del_event_info.first().event_name,
                                                                 del_event_info.first().event_code))

                            # stockevent 테이블 업데이트 - 삭제 종목
                            del_event_id = del_event_info.first().stock_event_id
                            del_event_info.delete()

                            # stockprice 테이블 업데이트 - 삭제 종목
                            del_event_price = PriceInfo.objects.filter(stock_event_id=del_event_id)
                            del_event_price.delete()

                            # 관리상태정보 삭제
                            del_event_status = InfoUpdateStatus.objects.filter(stock_event_id=del_event_id)
                            del_event_status.delete()

                # stockevent 테이블 업데이트 - 신규 종목
                # db에 넣을 데이터 구성
                # new_event_insert_db = [{'event_code': new_event_code, 'event_name': new_event_name}
                #                        for new_event_code, new_event_name in new_event_result.items()]
                # with transaction.atomic():
                #     for item in new_event_insert_db:
                #         entry = EventInfo(**item)
                #         entry.save()

                # eventinfo/priceinfo 테이블 업데이트 - 기존종목과 신규종목
                for k, v in price_info_df.to_dict('index').items():
                    with transaction.atomic():
                        # 특정 코드 테스트 시 사용
                        if BATCH_TEST_CODE_YN:
                            if k not in BATCH_TEST_CODE_LIST:
                                continue

                        new_event_yn = False
                        # stockevent 테이블 업데이트 - 신규 종목
                        if k in new_event_result:
                            entry = EventInfo(**{'event_code': k, 'event_name': new_event_result[k]})
                            entry.save()
                            new_event_yn = True

                        event_info = EventInfo.objects.filter(event_code=k)
                        if event_info.count() == 0:  # 가격정보는 존재하나 krx 종목정보에 등록되어 있지 않은 경우 UPDATE 취소
                            logger.error('KRX 종목 정보에 등록되어 있지 않음. code = {}'.format(k))
                            continue
                        logger.debug('기존/신규종목 UPDATE : {} / {}'.format(k, event_info.first().event_name))

                        if new_event_yn:  # 신규종목이면 현재까지의 모든 정보 insert
                            price_info_df = stock.get_market_ohlcv_by_date(fromdate='19000101', todate=today,
                                                                           ticker=k)
                            price_info_df = price_info_df.replace({np.nan: None})
                            price_info_df = price_info_df.reset_index()
                            price_info_df.rename(
                                columns={'날짜': 'date', '시가': 'open', '종가': 'close', '거래량': 'volume', '고가': 'high',
                                         '저가': 'low',
                                         '거래대금': 'value', '등락률': 'up_down_rate'},
                                inplace=True)
                            # stockprice 테이블에 insert
                            with transaction.atomic():
                                for priceitem in price_info_df.to_dict('records'):
                                    if priceitem['open'] != 0 and priceitem['high'] != 0 \
                                            and priceitem['low'] != 0 and priceitem['close'] != 0:
                                        entry = PriceInfo(**priceitem)
                                        entry.stock_event_id = event_info.first().stock_event_id
                                        entry.save()
                        else:  # 기존종목이면 updateStatus를 확인하여 누락된 경우를 체크 후 INSERT 및 UPDATE
                            event_status = InfoUpdateStatus.objects.filter(
                                stock_event_id=event_info.first().stock_event_id)

                            if (today_org - timedelta(
                                    days=1)).date() > event_status.first().mod_dt:  # 실행날짜를 제외하고 1일이상 누락된 경우
                                logger.debug('실행날짜를 제외하고 1일이상 누락된 경우')
                                # 실행날짜를 제외한 업데이트 빠진 기간 insert
                                fromdate = (event_status.first().mod_dt + timedelta(days=1)).strftime('%Y%m%d')
                                todate = (today_org - timedelta(days=1)).strftime('%Y%m%d')
                                omit_price_info_df = stock.get_market_ohlcv_by_date(fromdate=fromdate,
                                                                                    todate=todate,
                                                                                    ticker=k)
                                if len(omit_price_info_df) != 0:  # 휴일에 의한 업데이트 시간차 발생 경우 제외
                                    omit_price_info_df = omit_price_info_df.reset_index()
                                    omit_price_info_df.rename(
                                        columns={'날짜': 'date', '시가': 'open', '종가': 'close', '거래량': 'volume',
                                                 '고가': 'high',
                                                 '저가': 'low',
                                                 '거래대금': 'value', '등락률': 'up_down_rate'},
                                        inplace=True)
                                    with transaction.atomic():
                                        for price_item in omit_price_info_df.to_dict('records'):
                                            # 종목이 비활성화된것으로 간주
                                            if price_item['open'] != 0 and price_item['high'] != 0 \
                                                    and price_item['low'] != 0 and price_item['close'] != 0:
                                                entry = PriceInfo(**price_item)
                                                entry.stock_event_id = event_info.first().stock_event_id
                                                entry.save()
                                logger.info('{} : updating omitted informations complete'.format(k))

                            if not holiday:
                                if event_status.first().mod_dt.strftime('%Y%m%d') == today:
                                    logger.info('금일 주가 UPDATE : code = {}'.format(k))
                                    # 장 끝난 시점에 하루에 한번만 업데이트하는거면 스킵하고, 하루에 여러번 업데이트하는거면 해당날짜의 주가 계속 받아와서 업데이트해야함.
                                    # -> 하루에 한번 실행이라도 처음 insert에 장중가가 반영될 경우를 대비해 업데이트하도록 함.
                                    today_event_info = PriceInfo.objects.filter(
                                        stock_event_id=event_info.first().stock_event_id, date=today_org)
                                    today_event_info.open = v['open']
                                    today_event_info.close = v['close']
                                    today_event_info.volume = v['volume']
                                    today_event_info.high = v['high']
                                    today_event_info.low = v['low']
                                    today_event_info.value = v['value']
                                    today_event_info.up_down_rate = v['up_down_rate']
                                    today_event_info.update()
                                # 종목이 비활성화된것으로 간주되면 NO INSERT
                                elif v['open'] != 0 and v['high'] != 0 and v['low'] != 0 and v['close'] != 0:
                                    logger.info('금일 주가 INSERT : code=' + k, )
                                    entry = PriceInfo(**v)
                                    entry.stock_event_id = event_info.first().stock_event_id
                                    entry.save()

                        event_status = InfoUpdateStatus.objects.filter(
                            stock_event_id=event_info.first().stock_event_id)
                        if len(event_status) == 0:
                            status_dict = {'table_type': 'P', 'mod_dt': datetime.now(), 'reg_dt': datetime.now(),
                                           'stock_event_id': event_info.first().stock_event_id}
                            event_status_insert = InfoUpdateStatus(**status_dict)
                            event_status_insert.save()
                        else:
                            # event_status.first().mod_dt = datetime.now()
                            # event_status.first().save()
                            event_status.update(mod_dt=datetime.now())
                        time.sleep(0.1)
        else:
            logger.info('first batch executing, so skip daily batch')

        logger.info('[manage_event_daily] end')

    except Exception as e:
        logger.exception('[manage_event_daily] error occured')


def manage_fundamental_daily():
    cur_datetime = datetime.now()
    cur_date_str = cur_datetime.strftime('%Y%m%d')
    cur_qt = calQuarter(cur_datetime)
    # cur_year = cur_datetime.strftime('%Y')
    market_event_info = krx.get_market_ticker_and_name(date=cur_date_str, market='ALL')

    for event_code, event_name in market_event_info.iteritems():
        if BATCH_TEST_CODE_YN:
            if event_code not in BATCH_TEST_CODE_LIST:
                continue
            else:
                print('TEST : {}/{}'.format(event_code, event_name))
        # fundamental table에서 현재종목의 가장 최근 분기 가져오기.
        event_info = EventInfo.objects.filter(event_code=event_code)
        if event_info.count() == 0:
            logger.info('[manage_fundamental_daily] 종목 정보가 존재하지 않음 event_code = {}, '
                        'event_name = {}'.format(event_code, event_name))
            continue
        recent_quarter = FundamentalInfo.objects.filter(stock_event_id=event_info.first().stock_event_id).order_by(
            '-quarter')[:1]

        scan_qt = None
        if recent_quarter.count() == 0:  # 등록된 재무정보가 아예없을경우
            # 가격정보에서 조회한 주가시작날짜를 첫번쨰 조회분기로 지정
            start_price_info = PriceInfo.objects.filter(
                stock_event_id=event_info.first().stock_event_id).order_by('date')[:1]
            scan_qt = calQuarter(start_price_info.first().date)
        else:
            scan_qt = calNextQuarter(recent_quarter.first().quarter)

        while cur_qt != scan_qt:
            logger.info('scan_qt = {}'.format(scan_qt))
            scan_date = datetime.strptime(scan_qt, '%Y%m')
            quarter_code = calQuarterCode(scan_date)
            finstate = DartManager.instance().get_dart().finstate_all(event_name, scan_date.year, quarter_code)
            logger.info('finstate = {}'.format(finstate))
            if finstate is not None:
                assets = int(finstate.loc[DartConfig().assets_condition(finstate)].iloc[0][DartConfig().column_amount])
                liabilities = int(
                    finstate.loc[DartConfig().liabilities_condition(finstate)].iloc[0][DartConfig().column_amount])
                equity = int(finstate.loc[DartConfig().equity_condition(finstate)].iloc[0][DartConfig().column_amount])
                revenue = int(
                    finstate.loc[DartConfig().revenue_condition(finstate)].iloc[0][DartConfig().column_amount])
                profit_loss = int(
                    finstate.loc[DartConfig().profit_loss_condition(finstate)].iloc[0][DartConfig().column_amount])
                operating_income_loss = int(
                    finstate.loc[DartConfig().operating_income_loss_condition(finstate)].iloc[0][
                        DartConfig().column_amount])
                profit_loss_control = int(finstate.loc[DartConfig().profit_loss_control_condition(finstate)].iloc[0][
                                              DartConfig().column_amount])
                profit_loss_non_control = int(
                    finstate.loc[DartConfig().profit_loss_non_control_condition(finstate)].iloc[0][
                        DartConfig().column_amount])
                profit_loss_before_tax = int(
                    finstate.loc[DartConfig().profit_loss_before_tax_condition(finstate)].iloc[0][
                        DartConfig().column_amount])
                eps = int(finstate.loc[DartConfig().eps_condition(finstate)].iloc[0][DartConfig().column_amount])
                investing_cash_flow = int(finstate.loc[DartConfig().investing_cash_flow_condition(finstate)].iloc[0][
                                              DartConfig().column_amount])
                operating_cash_flow = int(finstate.loc[DartConfig().operating_cash_flow_condition(finstate)].iloc[0][
                                              DartConfig().column_amount])
                financing_cash_flow = int(finstate.loc[DartConfig().financing_cash_flow_condition(finstate)].iloc[0][
                                              DartConfig().column_amount])

                if quarter_code == '11011':  # 사업보고서의 경우 1,2,3분기를 합산한 금액을 감액해야 4분기 계산가능
                    recent_quarter = FundamentalInfo.objects.filter(stock_event_id=event_info.first().stock_event_id) \
                        .filter(quarter__startswith=str(scan_date.year))
                    for item in recent_quarter:
                        assets -= item.assets
                        liabilities -= item.liabilities
                        equity -= item.equity
                        revenue -= item.revenue
                        operating_income_loss -= item.operating_income_loss
                        profit_loss -= item.profit_loss
                        profit_loss_control -= item.profit_loss_control
                        profit_loss_non_control -= item.profit_loss_non_control
                        profit_loss_before_tax -= item.profit_loss_before_tax
                        eps -= item.eps
                        investing_cash_flow -= item.investing_cash_flow
                        operating_cash_flow -= item.operating_cash_flow
                        financing_cash_flow -= item.financing_cash_flow

                entry = FundamentalInfo(**{'stock_event_id': event_info.first().stock_event_id, 'quarter': scan_qt,
                                           'assets': assets, 'liabilities': liabilities, 'equity': equity,
                                           'revenue': revenue, 'operating_income_loss': operating_income_loss,
                                           'profit_loss': profit_loss, 'profit_loss_control': profit_loss_control,
                                           'profit_loss_non_control': profit_loss_non_control,
                                           'profit_loss_before_tax': profit_loss_before_tax, 'eps': eps,
                                           'investing_cash_flow': investing_cash_flow,
                                           'operating_cash_flow': operating_cash_flow,
                                           'financing_cash_flow': financing_cash_flow})
                entry.save()
            # 다음 분기 계산
            scan_qt = calNextQuarter(scan_qt)


def calQuarter(quarter_date):
    quarter = str(math.ceil(quarter_date.month / 3.0))
    quarter_month = None
    if quarter == '1':
        quarter_month = '03'
    elif quarter == '2':
        quarter_month = '06'
    elif quarter == '3':
        quarter_month = '09'
    elif quarter == '4':
        quarter_month = '12'
    return str(quarter_date.year)+quarter_month


def calQuarterCode(quarter_date):
    quarter = str(math.ceil(quarter_date.month / 3.0))
    if quarter == '1':
        return '11013'
    elif quarter == '2':
        return '11012'
    elif quarter == '3':
        return '11014'
    elif quarter == '4':
        return '11011'


def calNextQuarter(qt):
    qt_origin = datetime.strptime(qt, '%Y%m')
    next_qt = qt_origin + relativedelta(months=3)
    return next_qt.strftime('%Y%m')

# def manage_event_all():
#     global first
#     global insert_all
#     today_org = datetime.now()
#     print('cur time = ',today_org)
#     today = today_org.strftime('%Y%m%d')
#
#     cur_event_info = StockEvent.objects.all()
#     start_date_str = datetime.now().strftime('%Y%m%d')
#     market_event_info = krx.get_market_ticker_and_name(date=start_date_str, market='ALL')
#
#     whole_code_df = [{'event_code': k, 'event_name': v} for k, v in market_event_info.iteritems()]
#
#     # 전체 기간 전체 종목 insert
#     if cur_event_info.count() == 0 or insert_all:
#         print('first batch start')
#         first = True
#         insert_all = False
#         # test code
#         # whole_code_df = [{'event_code': '005930'}]
#
#         get_market_data_time_taken = 0.0
#         insert_market_data_time_taken = 0.0
#         insert_count = 0
#         for item in whole_code_df:
#             event_code = item['event_code']
#             # 기존 등록된 종목인지 확인.
#             event_info = StockEvent.objects.filter(event_code=event_code)
#             if event_info.count() != 0:
#                 event_status = StockInfoUpdateStatus.objects.filter(stock_event_id=event_info.first().stock_event_id)
#                 if event_status.count() != 0: # 이미 등록된 것이면 스킵.
#                     print(item['event_code'],' already inserted. skip inserting.')
#                     continue
#                 else: # 종목정보 INSERT 중, 비정상종료된 케이스로 간주하고 해당 종목정보들 삭제 후 재등록
#                     print(item['event_code'],' already inserted. but not completed. delete and re-insert.')
#                     event_price = StockPrice.objects.filter(stock_event_id=event_info.first().stock_event_id)
#                     event_info.delete()
#                     event_price.delete()
#
#             insert_count += 1
#             print(item['event_code'],' inserting.. inserting count = ',insert_count)
#             # stockevent 테이블에 insert
#             with transaction.atomic():
#                 entry = StockEvent(**item)
#                 entry.save()
#
#             # print('event_code = ', event_code)
#             event_info = StockEvent.objects.filter(event_code=event_code)
#             start_get_market_data = datetime.now().timestamp()
#
#             price_info_df = stock.get_market_ohlcv_by_date(fromdate='19000101', todate=today, ticker=event_code)
#             # print('price_info = ', price_info_df)
#             end_get_market_data = datetime.now().timestamp()
#             get_market_data_time_taken += (end_get_market_data - start_get_market_data)
#
#             price_info_df = price_info_df.reset_index()
#             price_info_df.rename(
#                 columns={'날짜': 'date', '시가': 'open', '종가': 'close', '거래량': 'volume', '고가': 'high', '저가': 'low',
#                          '거래대금': 'value', '등락률': 'up_down_rate'},
#                 inplace=True)
#
#             # stockprice 테이블에 insert
#             with transaction.atomic():
#                 for priceitem in price_info_df.to_dict('records'):
#                     # if StockPrice.objects.filter(date=item['date']).filter(event_code=event_info.event_code).count() < 1:
#                     entry = StockPrice(**priceitem)
#                     entry.stock_event_id = event_info.first().stock_event_id
#                     entry.save()
#
#             end_insert_market_data = datetime.now().timestamp()
#             insert_market_data_time_taken += (end_insert_market_data - end_get_market_data)
#
#             status_dict = {'table_type': 'P', 'mod_dt': datetime.now(), 'reg_dt': datetime.now(),
#                            'stock_event_id': event_info.first().stock_event_id}
#             event_status_insert = StockInfoUpdateStatus(**status_dict)
#             event_status_insert.save()
#
#         print('get market data time = ', get_market_data_time_taken)
#         print('insert market data time = ', insert_market_data_time_taken)
#         print('end insert stock data')
#         first = False
#
#     # 하루단위 전체종목 insert
#     else:
#         print('daily batch start')
#         print('first_batch executing status = ',first)
#         if not first:
#             price_info_df = stock.get_market_ohlcv_by_ticker(date=today, market='ALL')
#             # 시가,종가,고가,저가 가 모두 0이면 휴일으로 간주하고 스킵.
#             holiday = (price_info_df[['시가', '고가', '저가', '종가']] == 0).all(axis=None)
#             if not holiday:
#                 new_event_result = {}
#                 del_event_result = []
#                 # delete 항목을 따로 나중에 제외시키기 위해 현재 등록되어있는 종목 미리 모두 다 넣어둠.
#                 for cur_event in cur_event_info:
#                     del_event_result.append(cur_event.event_code)
#                 # 등록되어있는 종목, 신규종목, 삭제될 종목 구분.
#                 for market_event_code, market_event_name in market_event_info.iteritems():
#                     code_exist = False
#                     code_new = False
#                     code_delete = False
#                     for cur_event in cur_event_info:
#                         if cur_event.event_code == market_event_code:
#                             code_exist = True
#                             # event_result['exist'].append(item['event_code'])
#                             # 현재 시장에서 존재하는 종목이 db에서 존재한다면 그 외에는 모두 삭제될 종목이라는 점을 이용하여 필터링.
#                             del_event_result.remove(market_event_code)
#
#                     if not code_exist:
#                         code_new = True
#                         new_event_result.update({market_event_code: market_event_name})
#
#                 # 삭제 종목 관리
#                 del_event_id_list = []
#                 with transaction.atomic():
#                     for delete_event_code in del_event_result:
#                         del_event_info = StockEvent.objects.filter(event_code=delete_event_code)
#                         if len(del_event_info) != 0:
#                             # stockevent 테이블 업데이트 - 삭제 종목
#                             del_event_info.delete()
#
#                             del_event_id = del_event_info.first().stock_event_id
#                             # stockprice 테이블 업데이트 - 삭제 종목
#                             del_event_price = StockPrice.objects.filter(stock_event_id=del_event_id)
#                             del_event_price.delete()
#
#                             # 관리상태정보 삭제
#                             del_event_status = StockInfoUpdateStatus.objects.filter(stock_event_id=del_event_id)
#                             del_event_status.delete()
#
#                 # stockevent 테이블 업데이트 - 신규 종목
#                 # db에 넣을 데이터 구성
#                 new_event_insert_db = [{'event_code': new_event_code, 'event_name': new_event_name}
#                                        for new_event_code, new_event_name in new_event_result.items()]
#                 with transaction.atomic():
#                     for item in new_event_insert_db:
#                         entry = StockEvent(**item)
#                         entry.save()
#
#                 # stockprice 테이블 업데이트 - 신규/기존 종목
#                 # price_info_df = price_info.reset_index() # 종목코드를 컬럼으로 빼기.
#                 price_info_df.rename(
#                     columns={'티커': 'event_code', '시가': 'open', '종가': 'close', '거래량': 'volume', '고가': 'high',
#                              '저가': 'low',
#                              '거래대금': 'value', '등락률': 'up_down_rate'}, inplace=True)
#                 price_info_df['date'] = datetime.now()
#
#                 with transaction.atomic():
#                     for k, v in price_info_df.to_dict('index').items():
#                         event_status = StockInfoUpdateStatus.objects.filter(event_code=k)
#                         event_info = StockEvent.objects.filter(event_code=k)
#
#                         if event_status.mod_dt.strftime('%Y%m%d') == today:
#                             # 장 끝난 시점에 하루에 한번만 업데이트하는거면 스킵하고, 하루에 여러번 업데이트하는거면 해당날짜의 주가 계속 받아와서 업데이트해야함.
#                             # 하루에 한번 실행이라도 처음 insert에 장중가가 반영될 경우를 대비해 업데이트하는게 좋은듯..?
#                             today_event_info = StockPrice.objects.filter(event_code=k, date=today)
#                             today_event_info.open = v['open']
#                             today_event_info.close = v['close']
#                             today_event_info.volume = v['volume']
#                             today_event_info.high = v['high']
#                             today_event_info.low = v['low']
#                             today_event_info.value = v['value']
#                             today_event_info.up_down_rate = v['up_down_rate']
#                             today_event_info.update()
#                             continue
#                         elif today_org - timedelta(days=1) > event_status.mod_dt: # 실행날짜를 제외하고 1일이상 누락된 경우
#                             # 업데이트 빠진 기간 insert
#                             fromdate = (event_status.mod_dt + timedelta(days=1)).strftime('%Y%m%d')
#                             todate = (today_org - timedelta(days=1)).strftime('%Y%m%d')
#                             omit_price_info_df = stock.get_market_ohlcv_by_date(fromdate=fromdate, todate=todate,
#                                                                            ticker=k)
#                             if len(omit_price_info_df) != 0: # 휴일에 의한 업데이트 시간차 발생 경우 제외
#                                 omit_price_info_df = omit_price_info_df.reset_index()
#                                 omit_price_info_df.rename(
#                                     columns={'날짜': 'date', '시가': 'open', '종가': 'close', '거래량': 'volume', '고가': 'high',
#                                              '저가': 'low',
#                                              '거래대금': 'value', '등락률': 'up_down_rate'},
#                                     inplace=True)
#                                 with transaction.atomic():
#                                     for priceitem in omit_price_info_df.to_dict('records'):
#                                         # if StockPrice.objects.filter(date=item['date']).filter(event_code=event_info.event_code).count() < 1:
#                                         entry = StockPrice(**priceitem)
#                                         entry.stock_event_id = event_info.first().stock_event_id
#                                         entry.save()
#
#                         entry = StockPrice(**v)
#                         entry.stock_event_id = event_info.first().stock_event_id
#                         entry.save()
#
#                         event_status = StockInfoUpdateStatus.objects.filter(
#                             stock_event_id=event_info.first().stock_event_id)
#                         if len(event_status) == 0:
#                             status_dict = {'table_type': 'P', 'mod_dt': datetime.now(), 'reg_dt': datetime.now(),
#                                            'stock_event_id': event_info.first().stock_event_id}
#                             event_status_insert = StockInfoUpdateStatus(**status_dict)
#                             event_status_insert.save()
#                         else:
#                             event_status.mod_dt = datetime.now()
#                             event_status.update()
#             else:
#                 print('it''s holiday. skip daily batch.')
#         else:
#             print('first batch executing, so skip daily batch')
#
#     print('end managing event job.')
