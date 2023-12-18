from ..models import PriceInfo, InfoUpdateStatus, EventInfo, NotAdjPriceInfo, FinancialIndicator, ForeignHoldingVol, \
    IndexBasicInfo, IndexContainMapInfo, IndexPriceInfo
from pykrx.website import krx
from pykrx import stock
import datetime
from dateutil.relativedelta import relativedelta
from django.db import transaction
import time
import numpy as np
from numpy.lib import math
import logging
from ..config.stockConfig import BATCH_TEST_CODE_YN, BATCH_TEST_CODE_LIST, SKIP_MANAGE_EVENT_INIT, \
    FIRST_BATCH_TODATE, FUND_API_REQUEST_TERM, FUND_SKIP_CO, FUND_SKIP_FINSTATE, \
    INDEX_DAILY_API_REQUEST_TERM, SKIP_MANAGE_INDEX_INFO
from ..custom.opendartreader.dart_manager import DartManager
from ..custom.opendartreader.dart_config import DartFinstateConfig, DartStockSharesConfig
from ..custom import pykrx as stock_custom
from .stock_batch_manager import StockBatchManager
from ..config.classificationCode import krxMarketCode, krxMarketStatusCode, dbTableType, dbUpdateType, \
    krxIndexMarketCode
import re

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
first = False  # naver api 첫 insert 진행중 여부
etc_first = False  # krx api 첫 insert 진행중 여부

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
    logger_method = '[manage_event_init] '
    try:
        logger.info('{}start'.format(logger_method))
        global first
        todate = FIRST_BATCH_TODATE
        todate_org = datetime.datetime.strptime(todate, '%Y%m%d')

        # cur_event_info = EventInfo.objects.all()
        start_date_str = datetime.datetime.now().strftime('%Y%m%d')
        market_event_info = krx.get_market_ticker_and_name(date=start_date_str, market='ALL')

        whole_code = [{'event_code': k, 'event_name': v} for k, v in market_event_info.iteritems()]
        # 전체 기간 전체 종목 insert
        if not SKIP_MANAGE_EVENT_INIT:
            logger.info('{}first batch start'.format(logger_method))
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
                    event_status = InfoUpdateStatus.objects.filter(class_id=event_info.first().stock_event_id) \
                        .filter(table_type=dbTableType('종목수정종가'))
                    if event_status.count() != 0:  # 이미 등록된 것이면 스킵.
                        logger.info('{}{} already inserted. skip inserting.'.format(logger_method, item['event_code']))
                        continue
                    else:  # 종목정보 INSERT 중, 비정상종료된 케이스로 간주하고 해당 종목정보들 삭제 후 재등록
                        logger.info(
                            '{}{} already inserted. but not completed. delete and re-insert.'
                                .format(logger_method, item['event_code']))
                        event_price = PriceInfo.objects.filter(stock_event_id=event_info.first().stock_event_id)
                        event_info.delete()
                        event_price.delete()

                # 신규종목일 경우에는 위의 로직을 무시하고, 기존정보가 없으므로 그냥 INSERT 된다.
                insert_count += 1
                logger.info(
                    '{}{} inserting.. inserting count = {}'.format(logger_method, item['event_code'], insert_count))
                # stockevent 테이블에 insert
                with transaction.atomic():
                    entry = EventInfo(**item)
                    entry.save()

                # print('event_code = ', event_code)
                event_info = EventInfo.objects.filter(event_code=event_code)
                start_get_market_data = datetime.datetime.now().timestamp()

                price_info_df = stock.get_market_ohlcv_by_date(fromdate='19000101', todate=todate, ticker=event_code)
                price_info_df = price_info_df.replace({np.nan: None})
                # print('price_info = ', price_info_df)
                end_get_market_data = datetime.datetime.now().timestamp()
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

                end_insert_market_data = datetime.datetime.now().timestamp()
                insert_market_data_time_taken += (end_insert_market_data - end_get_market_data)

                status_dict = {'table_type': dbTableType('종목수정종가'), 'mod_dt': todate_org, 'reg_dt': todate_org,
                               'update_type': 'U',
                               'class_id': event_info.first().stock_event_id}
                event_status_insert = InfoUpdateStatus(**status_dict)
                event_status_insert.save()

            logger.info('{}get market data time = {}'.format(logger_method, get_market_data_time_taken))
            logger.info('{}insert market data time = {}'.format(logger_method, insert_market_data_time_taken))
            logger.info('{}end'.format(logger_method))
        else:
            logger.info('{}skip.'.format(logger_method))
    except Exception as e:
        logger.exception('{}error occured'.format(logger_method))
    finally:
        first = False


def manage_event_daily():
    logger_method = '[manage_event_daily] '
    try:
        logger.info('{}start'.format(logger_method))
        global first
        today_org = datetime.datetime.now()
        logger.debug('{}cur time = {}'.format(logger_method, str(today_org)))
        today = today_org.strftime('%Y%m%d')

        cur_event_info = EventInfo.objects.all()
        start_date_str = datetime.datetime.now().strftime('%Y%m%d')
        market_event_info = krx.get_market_ticker_and_name(date=start_date_str, market='ALL')

        whole_code_df = [{'event_code': k, 'event_name': v} for k, v in market_event_info.iteritems()]
        # manage_event_init과 같이 종목을 모두 insert하지 않더라도 skip할수 있어야함.
        # 하루단위 전체종목 insert
        if cur_event_info.count() != 0:
            logger.info('{}first_batch executing status = {}'.format(logger_method, first))
            if not first:
                price_info_df = stock.get_market_ohlcv_by_ticker(date=today, market='ALL')
                # 전체종목에 대해 시가,종가,고가,저가 가 모두 0이면 휴일으로 간주하고 스킵.
                holiday = (price_info_df[['시가', '고가', '저가', '종가']] == 0).all(axis=None)
                # stockprice 테이블 업데이트 - 신규/기존 종목
                # price_info_df = price_info.reset_index() # 종목코드를 컬럼으로 빼기.
                price_info_df = price_info_df.replace({np.nan: None})
                price_info_df.rename(
                    columns={'시가': 'open', '종가': 'close', '거래량': 'volume', '고가': 'high',
                             '저가': 'low', '거래대금': 'value', '등락률': 'up_down_rate',
                             }, inplace=True)

                price_info_df['date'] = datetime.datetime.now()

                # if not holiday:
                new_event_result = {}
                del_event_result = []
                if not SKIP_MANAGE_EVENT_INIT:  # 현재 DB에 등록된 종목을 기준으로 업데이트 테스트하기 위해 삭제/신규종목 초기화
                    # delete 항목을 따로 나중에 제외시키기 위해 현재 등록되어있는 종목 미리 모두 다 넣어둠.
                    if len(market_event_info) != 0:
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
                                # DB 에서 존재하는 종목 중 시장에서 존재하는 종목 말고는 모두 제거되어야 하는 종목임.
                                del_event_result.remove(market_event_code)

                        if not code_exist:
                            code_new = True
                            new_event_result.update({market_event_code: market_event_name})

                for delete_event_code in del_event_result:
                    with transaction.atomic():
                        del_event_info = EventInfo.objects.filter(event_code=delete_event_code)
                        if len(del_event_info) != 0:
                            logger.info('{}종목 삭제 : {} / {}'.format(logger_method, del_event_info.first().event_name,
                                                                   del_event_info.first().event_code))

                            # stockevent 테이블 업데이트 - 삭제 종목
                            del_event_id = del_event_info.first().stock_event_id
                            del_event_info.delete()

                            # stockprice 테이블 업데이트 - 삭제 종목
                            del_event_price = PriceInfo.objects.filter(stock_event_id=del_event_id)
                            del_event_price.delete()

                            # 관리상태정보 삭제
                            del_event_status = InfoUpdateStatus.objects.filter(class_id=del_event_id) \
                                .filter(table_type=dbTableType('종목수정종가'))
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
                            # logger.error('{}KRX 종목 정보에 등록되어 있지 않음. code = {}'.format(logger_method, k))
                            continue
                        logger.debug('{}기존/신규종목 UPDATE : {} / {}'.format(
                            logger_method, k, event_info.first().event_name))

                        fromdate = None
                        before_insert_yn = False  # 누락된 경우 또는 신규종목일경우에 이전날짜 업데이트 여부
                        if new_event_yn:  # 신규종목이면 실행날짜 이전까지의 모든 정보 insert
                            fromdate = '19000101'
                            before_insert_yn = True
                        else:  # 기존종목이면 updateStatus를 확인하여 누락된 경우를 체크 후 INSERT 및 UPDATE
                            event_status = InfoUpdateStatus.objects.filter(
                                class_id=event_info.first().stock_event_id).filter(
                                table_type=dbTableType('종목수정종가'))

                            if (today_org - datetime.timedelta(
                                    days=1)).date() > event_status.first().mod_dt:  # 실행날짜를 제외하고 1일이상 누락된 경우
                                logger.debug('{}실행날짜를 제외하고 1일이상 누락된 경우'.format(logger_method))
                                # 실행날짜를 제외한 업데이트 빠진 기간 insert
                                fromdate = (event_status.first().mod_dt + datetime.timedelta(days=1)).strftime('%Y%m%d')
                                before_insert_yn = True

                        if before_insert_yn:
                            todate = (today_org - datetime.timedelta(days=1)).strftime('%Y%m%d')
                            omit_price_info_df = stock.get_market_ohlcv_by_date(fromdate=fromdate,
                                                                                todate=todate,
                                                                                ticker=k)
                            time.sleep(0.1)
                            if len(omit_price_info_df) != 0:  # 휴일에 의한 업데이트 시간차 발생 경우 제외
                                omit_price_info_df = omit_price_info_df.replace({np.nan: None})
                                omit_price_info_df = omit_price_info_df.reset_index()
                                omit_price_info_df.rename(
                                    columns={'날짜': 'date', '시가': 'open', '종가': 'close', '거래량': 'volume',
                                             '고가': 'high', '저가': 'low', '거래대금': 'value', '등락률': 'up_down_rate'},
                                    inplace=True)
                                with transaction.atomic():
                                    for price_item in omit_price_info_df.to_dict('records'):
                                        # 종목이 비활성화된것으로 간주되면 NO INSERT
                                        if price_item['open'] != 0 and price_item['high'] != 0 \
                                                and price_item['low'] != 0 and price_item['close'] != 0:
                                            entry = PriceInfo(**price_item)
                                            entry.stock_event_id = event_info.first().stock_event_id
                                            entry.save()
                            logger.info('{}{} : updating omitted informations complete'.format(logger_method, k))

                        if not holiday:
                            if not new_event_yn:
                                event_status = InfoUpdateStatus.objects.filter(
                                    class_id=event_info.first().stock_event_id).filter(
                                    table_type=dbTableType('종목수정종가'))
                                if event_status.first().mod_dt.strftime('%Y%m%d') == today:
                                    logger.info('{}금일 UPDATE 됨. skip'.format(logger_method))
                                    # logger.info('{}금일 UPDATE : code = {}'.format(logger_method, k))
                                    # 장 끝난 시점에 하루에 한번만 업데이트하는거면 스킵하고, 하루에 여러번 업데이트하는거면 해당날짜의 주가 계속 받아와서 업데이트해야함.
                                    # -> 하루에 한번 실행이라도 처음 insert에 장중가가 반영될 경우를 대비해 업데이트하도록 함.
                                    # today_price_info = PriceInfo.objects.filter(
                                    #     stock_event_id=event_info.first().stock_event_id, date=today_org)
                                    # today_price_info.open = v['open']
                                    # today_price_info.close = v['close']
                                    # today_price_info.volume = v['volume']
                                    # today_price_info.high = v['high']
                                    # today_price_info.low = v['low']
                                    # today_price_info.value = v['value']
                                    # today_price_info.up_down_rate = v['up_down_rate']
                                    # today_price_info.update()
                                    """
                                    일단 하루에 한번만 가져오는 것으로 하고 pass 하기 - 장 마감 이후에 INSERT를 하도록 해야함!
                                    """
                                    pass
                                # 주가 가격정보가 없어서 종목이 비활성화된것(거래정지 등) 으로 간주되면 NO INSERT
                                elif v['open'] != 0 and v['high'] != 0 and v['low'] != 0 and v['close'] != 0:
                                    logger.info('{}금일 INSERT : code={}'.format(logger_method, k))
                                    entry = PriceInfo(**v)
                                    entry.stock_event_id = event_info.first().stock_event_id
                                    entry.save()

                            # 새 상장 종목 : UPDATE 할 필요가 없음.
                            # 주가 가격정보가 없어서 종목이 비활성화된것(거래정지 등) 으로 간주되면 NO INSERT
                            elif v['open'] != 0 and v['high'] != 0 and v['low'] != 0 and v['close'] != 0:
                                logger.info('{}금일 INSERT : code={}'.format(logger_method, k))
                                entry = PriceInfo(**v)
                                entry.stock_event_id = event_info.first().stock_event_id
                                entry.save()

                            # 시장명 다르거나 없다면 업데이트

                        event_status = InfoUpdateStatus.objects.filter(
                            class_id=event_info.first().stock_event_id).filter(table_type=dbTableType('종목수정종가'))
                        if len(event_status) == 0:
                            status_dict = {'table_type': dbTableType('종목수정종가'), 'mod_dt': today_org,
                                           'reg_dt': today_org,
                                           'update_type': 'U', 'class_id': event_info.first().stock_event_id}
                            event_status_insert = InfoUpdateStatus(**status_dict)
                            event_status_insert.save()
                        else:
                            # event_status.first().mod_dt = datetime.datetime.now()
                            # event_status.first().save()
                            event_status.update(mod_dt=datetime.datetime.now())

            else:
                logger.info('{}manage_event_init executing, so skip daily batch'.format(logger_method))

        logger.info('{}end'.format(logger_method))

    except Exception as e:
        logger.exception('{}error occured'.format(logger_method))


def manage_financial_indicator_daily():
    global first
    logger_method = '[manage_financial_indicator_daily] '
    try:
        logger.info('{}start'.format(logger_method))
        if not first:
            today_org = datetime.datetime.now()
            logger.debug('{}cur time = {}'.format(logger_method, str(today_org)))
            today = today_org.strftime('%Y%m%d')

            cur_event_info = EventInfo.objects.all()
            cur_event_info_list = []
            for cur_event in cur_event_info:
                cur_event_info_list.append(cur_event.stock_event_id)
            # manage_event_init과 같이 종목을 모두 insert하지 않더라도 skip할수 있어야함.

            indicator_id_list = FinancialIndicator.objects.distinct().values_list('stock_event_id')
            for indicator_tuple in indicator_id_list:
                indicator_event_id = indicator_tuple[0]  # distinct를 이용하면 결과값이 tuple이 된다. 그중 처음값 이용.
                if indicator_event_id not in cur_event_info_list:
                    # 현재 DB 종목리스트에 등록되어있는 종목이 아니라면 삭제하기
                    delete_qryset = FinancialIndicator.objects.filter(stock_event_id=indicator_event_id)
                    delete_qryset.delete()

            # # 가장 최근의 일괄처리 처리 날짜 조회하여 해당날짜 이후부터 INSERT (누락건에 대해 체크)
            # mod_dt를 내림차순으로 정렬
            event_status = InfoUpdateStatus.objects.filter(table_type=dbTableType('지표')).distinct().values_list(
                'mod_dt').order_by(
                '-mod_dt')[:1]

            scan_date = None
            if event_status.count() != 0:  # 최근날짜부터 INSERT 이므로 일배치 시작날짜 이전데이터를 가져올 경우는 없다.
                scan_date = event_status.first()[0]
            else:  # init 배치를 실행하지 않고 daily 배치만 실행하는경우 오늘날짜부터 insert
                scan_date = (today_org - datetime.timedelta(days=1)).date()
            # 하루단위 전체종목 insert
            while scan_date != today_org.date():  # 날짜별 insert
                scan_date += datetime.timedelta(days=1)
                scan_date_str = scan_date.strftime('%Y%m%d')
                indic_info_df = stock.get_market_fundamental_by_ticker(date=scan_date_str, market='ALL')
                if indic_info_df is None or len(indic_info_df) == 0:
                    logger.error('{}get empty data. quit.'.format(logger_method))
                    return

                holiday = (indic_info_df[['BPS', 'PER', 'PBR', 'EPS', 'DIV', 'DPS']] == 0).all(
                    axis=None)
                if holiday:
                    continue

                indic_info_df = indic_info_df.replace({np.nan: None})
                indic_info_df.rename(
                    columns={'BPS': 'bps', 'PER': 'per', 'PBR': 'pbr', 'EPS': 'eps', 'DIV': 'div', 'DPS': 'dps'},
                    inplace=True)
                indic_info_df['date'] = scan_date
                with transaction.atomic():
                    for k, v in indic_info_df.to_dict('index').items():
                        # 특정 코드 테스트 시 사용
                        if BATCH_TEST_CODE_YN:
                            if k not in BATCH_TEST_CODE_LIST:
                                continue
                        event_info = EventInfo.objects.filter(event_code=k)
                        if event_info.count() == 0:  # 정보는 존재하나 krx 종목정보에 등록되어 있지 않은 경우 UPDATE 취소
                            # logger.error('{}KRX 종목 정보에 등록되어 있지 않음. code = {}'.format(logger_method, k))
                            continue

                        v['pbr'] = round(v['pbr'], 2)
                        v['per'] = round(v['per'], 2)
                        v['div'] = round(v['div'], 2)
                        entry = FinancialIndicator(**v)
                        entry.stock_event_id = event_info.first().stock_event_id
                        entry.save()

                    event_status = InfoUpdateStatus.objects.filter(table_type=dbTableType('지표'))
                    if len(event_status) == 0:
                        status_dict = {'table_type': dbTableType('지표'), 'mod_dt': scan_date, 'reg_dt': scan_date,
                                       'update_type': 'U'}
                        event_status_insert = InfoUpdateStatus(**status_dict)
                        event_status_insert.save()
                    else:
                        event_status.update(mod_dt=scan_date)

        else:
            logger.info('{}manage_event_init executing, so skip daily batch'.format(logger_method))

        logger.info('{}end'.format(logger_method))

    except Exception as e:
        logger.exception('{}error occured'.format(logger_method))


def manage_foreign_holding_daily():
    global first
    logger_method = '[manage_foreign_holding_daily] '
    try:
        logger.info('{}start'.format(logger_method))
        if not first:
            today_org = datetime.datetime.now()
            logger.debug('{}cur time = {}'.format(logger_method, str(today_org)))
            today = today_org.strftime('%Y%m%d')

            cur_event_info = EventInfo.objects.all()
            cur_event_info_list = []
            for cur_event in cur_event_info:
                cur_event_info_list.append(cur_event.stock_event_id)
            # manage_event_init과 같이 종목을 모두 insert하지 않더라도 skip할수 있어야함.

            id_list = ForeignHoldingVol.objects.distinct().values_list('stock_event_id')
            for id_tuple in id_list:
                event_id = id_tuple[0]  # distinct를 이용하면 결과값이 tuple이 된다. 그중 처음값 이용.
                if event_id not in cur_event_info_list:
                    # 현재 DB 종목리스트에 등록되어있는 종목이 아니라면 삭제하기
                    delete_qryset = ForeignHoldingVol.objects.filter(stock_event_id=event_id)
                    if delete_qryset.count() != 0:
                        delete_qryset.delete()

            # # 가장 최근의 일괄처리 처리 날짜 조회하여 해당날짜 이후부터 INSERT (누락건에 대해 체크)
            # mod_dt를 내림차순으로 정렬
            event_status = InfoUpdateStatus.objects.filter(table_type=dbTableType('외국인보유')).distinct().values_list(
                'mod_dt').order_by(
                '-mod_dt')[:1]

            scan_date = None
            if event_status.count() != 0:  # 최근날짜부터 INSERT 이므로 일배치 시작날짜 이전데이터를 가져올 경우는 없다.
                scan_date = event_status.first()[0]
            else:  # init 배치를 실행하지 않고 daily 배치 처음 실행하는경우 최근 일주일간 데이터를 가져오기.
                scan_date = (today_org - datetime.timedelta(days=8)).date()
            # 하루단위 전체종목 insert
            while scan_date != today_org.date():  # 날짜별 insert
                scan_date += datetime.timedelta(days=1)
                scan_date_str = scan_date.strftime('%Y%m%d')
                info_df = None
                try:
                    info_df = stock_custom.get_exhaustion_rates_of_foreign_investment_by_ticker(date=scan_date_str,
                                                                                                market='ALL')
                except Exception as e:
                    logger.error('{}get data error. date={}, error message={}'.format(logger_method, scan_date_str, e))
                if info_df is None or len(info_df) == 0:
                    logger.error('{}get empty data. date={} skip.'.format(logger_method, scan_date_str))
                    continue

                # 휴일에는 데이터 자체가 아예 없음.
                # holiday = (info_df[['BPS', 'PER', 'PBR', 'EPS', 'DIV', 'DPS']] == 0).all(
                #     axis=None)
                # if holiday:
                #     continue

                info_df = info_df.replace({np.nan: None})
                info_df = info_df[['보유수량', '지분율', '한도수량', '한도소진률']]
                info_df.rename(
                    columns={'보유수량': 'hold_quantity', '지분율': 'sharehold_rate',
                             '한도수량': 'limit_quantity', '한도소진률': 'limit_exhaustion_rate'},
                    inplace=True)
                info_df['date'] = scan_date
                with transaction.atomic():
                    for k, v in info_df.to_dict('index').items():
                        # 특정 코드 테스트 시 사용
                        if BATCH_TEST_CODE_YN:
                            if k not in BATCH_TEST_CODE_LIST:
                                continue
                        event_info = EventInfo.objects.filter(event_code=k)
                        if event_info.count() == 0:  # 정보는 존재하나 krx 종목정보에 등록되어 있지 않은 경우 UPDATE 취소
                            # logger.error('{}KRX 종목 정보에 등록되어 있지 않음. code = {}'.format(logger_method, k))
                            continue

                        entry = ForeignHoldingVol(**v)
                        entry.stock_event_id = event_info.first().stock_event_id
                        entry.save()

                    event_status = InfoUpdateStatus.objects.filter(table_type=dbTableType('외국인보유'))
                    if len(event_status) == 0:
                        status_dict = {'table_type': dbTableType('외국인보유'), 'mod_dt': scan_date, 'reg_dt': scan_date,
                                       'update_type': 'U'}
                        event_status_insert = InfoUpdateStatus(**status_dict)
                        event_status_insert.save()
                    else:
                        event_status.update(mod_dt=scan_date)

        else:
            logger.info('{}manage_event_init executing, so skip daily batch'.format(logger_method))

        logger.info('{}end'.format(logger_method))

    except Exception as e:
        logger.exception('{}error occured'.format(logger_method))


def manage_index_daily():
    logger_method = '[manage_index_daily] '
    try:
        logger.info('{}start'.format(logger_method))
        today_org = datetime.datetime.now()
        logger.info('{}cur time = {}'.format(logger_method, str(today_org)))
        today = today_org.strftime('%Y%m%d')

        market_list = ["KOSPI", "KOSDAQ", "KRX", "테마"]
        for market in market_list:
            logger.info('{}manage for market {}'.format(logger_method, market))
            market_index_list = []
            try:
                market_index_list = stock.get_index_ticker_list(today, market)
            except Exception as e:
                logger.error('{}get index ticker list error, market={}, e={}'.format(logger_method, market, e))
            if len(market_index_list) == 0:
                logger.error(
                    '{}empty index list. skip for protect db data. market={}'.format(logger_method, market))
                continue

            # 신규 및 삭제종목 추리기.
            new_index_list = []
            del_index_list = []
            exi_index_list = []

            # 테스트를 위한 신규 및 삭제종목 관련 작업 스킵여부
            if not SKIP_MANAGE_INDEX_INFO:
                regist_index_qryset_by_market = IndexBasicInfo.objects.filter(mkt_code=krxIndexMarketCode(market))
                if regist_index_qryset_by_market.count() == 0:  # 처음 등록될 경우에는 모두다 INSERT
                    new_index_list.extend(market_index_list)
                else:
                    del_index_list.extend(market_index_list)  # 모두다 추가한다음 소거법으로 진행
                    for market_index_code in market_index_list:
                        code_exist = False
                        code_new = False
                        for regist_index in regist_index_qryset_by_market:
                            if regist_index.index_code == market_index_code:
                                code_exist = True
                                exi_index_list.append(market_index_code)
                                # DB 에서 존재하는 종목 중 시장에서 존재하는 종목 말고는 모두 제거되어야 하는 종목임.
                                del_index_list.remove(market_index_code)

                        if not code_exist:  # 시장 항목중 DB에 등록된 종목이 아니라면 신규종목으로 간주
                            code_new = True
                            new_index_list.append(market_index_code)
                with transaction.atomic():
                    # 시장에서 삭제된 지수 db에서 삭제
                    for del_code in del_index_list:
                        del_index_qryset = IndexBasicInfo.objects.filter(event_code=del_code)
                        if del_index_qryset.count() != 0:
                            logger.info('{}지수 삭제 : {} / {}'.format(logger_method,
                                                                   del_index_qryset.first().index_code,
                                                                   del_index_qryset.first().index_nm))
                            # indexbasic 테이블 업데이트 - 삭제 종목
                            del_index_id = del_index_qryset.first().del_index_id
                            del_index_qryset.delete()

                            # index contain map info 업데이트 - 삭제 종목
                            del_index_contain_map = IndexContainMapInfo.objects.filter(
                                stock_index_id=del_index_id)
                            del_index_contain_map.delete()

                            # stockprice 테이블 업데이트 - 삭제 종목
                            del_index_price = IndexPriceInfo.objects.filter(stock_index_id=del_index_id)
                            del_index_price.delete()

                            # 관리상태정보 삭제 - 시장종류별로 관리되므로 지수별 관리 필요없음.
                            # del_event_status = InfoUpdateStatus.objects.filter(class_id=del_index_id) \
                            #     .filter(table_type=dbTableType('지수가'))
                            # del_event_status.delete()

                    # 신규 지수에 대해 insert 작업 진행
                    for new_index_code in new_index_list:
                        name = stock.get_index_ticker_name(new_index_code)
                        logger.info('{}지수 INSERT : {} / {}'.format(logger_method, new_index_code, name))
                        pattern = r'[^a-zA-Z0-9가-힣]'
                        # 특수문자를 공백으로 치환
                        index_dense_nm = re.sub(pattern, '', name)
                        v = {'index_code': new_index_code, 'index_nm': name,
                             'index_dense_nm': index_dense_nm,
                             'mkt_code': krxIndexMarketCode(market)}
                        entry = IndexBasicInfo(**v)
                        entry.save()

                    # 업데이트된 모든 지수에 대해 구성지수종목 업데이트 및 삭제.
                    for market_index_code in market_index_list:
                        regist_index_qryset = IndexBasicInfo.objects.filter(index_code=market_index_code)
                        if regist_index_qryset.count() == 0:
                            logger.error('index is not synchronized with db. skip.')
                            continue
                        # if market_index_code not in new_index_list and market_index_code not in exi_index_list:
                        #     logger.error('index is not synchronized with db. skip.')
                        #     continue
                        logger.info('{}지수구성종목 UPDATE : {} / {}'.format(logger_method,
                                                                       regist_index_qryset.first().index_code,
                                                                       regist_index_qryset.first().index_nm))
                        market_event_list = []
                        try:
                            market_event_list = stock.get_index_portfolio_deposit_file(date=today,
                                                                                       ticker=market_index_code)
                            time.sleep(INDEX_DAILY_API_REQUEST_TERM)
                        except Exception as e:
                            logger.error('{}get event ticker list error, market={}, index={}, e={}'
                                         .format(logger_method, market, market_index_code, e))
                        if len(market_event_list) == 0:
                            logger.error('{}empty event list. skip for protect db data. market={}, index={}'
                                         .format(logger_method, market, market_index_code))
                            continue

                        new_event_list = []
                        del_event_list = []
                        regist_event_qryset = IndexContainMapInfo.objects.filter(
                            stock_index_id=regist_index_qryset.first().stock_index_id)
                        if regist_event_qryset.count() == 0:  # 처음 등록될 경우에는 모두다 INSERT
                            new_event_list.extend(market_event_list)
                        else:
                            del_event_list.extend(market_event_list)  # 모두다 추가한다음 소거법으로 진행
                            for market_event_code in market_event_list:
                                code_exist = False
                                code_new = False
                                for regist_event in regist_event_qryset:
                                    if regist_event.event_code == market_event_code:
                                        code_exist = True
                                        # DB 에서 존재하는 종목 중 시장에서 존재하는 종목 말고는 모두 제거되어야 하는 종목임.
                                        del_event_list.remove(market_event_code)

                                if not code_exist:  # 시장 항목중 DB에 등록된 종목이 아니라면 신규종목으로 간주
                                    code_new = True
                                    new_event_list.append(market_event_code)

                        # 삭제될 지수구성종목 모두 조회 및 삭제.
                        del_event_qryset = IndexContainMapInfo.objects.filter(
                            stock_index_id=regist_index_qryset.first().stock_index_id).filter(
                            event_code__in=del_event_list)
                        del_event_qryset.delete()

                        # 신규 지수구성종목에 대해 insert 작업 진행
                        for new_event_code in new_event_list:
                            v = {'stock_index_id': regist_index_qryset.first().stock_index_id,
                                 'event_code': new_event_code}
                            entry = IndexContainMapInfo(**v)
                            entry.save()

            # # 가장 최근의 일괄처리 처리 날짜 조회하여 해당날짜 이후부터 INSERT (누락건에 대해 체크)
            # mod_dt를 내림차순으로 정렬
            # stock_event_id_item = [krxIndexMarketCode(market), '#']
            # status_stock_event_id = ''.join(stock_event_id_item)
            event_status = InfoUpdateStatus.objects.filter(table_type=dbTableType('지수가')).filter(
                class_id=krxIndexMarketCode(market)).distinct().values_list('mod_dt').order_by(
                '-mod_dt')[:1]

            scan_date = None
            if event_status.count() != 0:  # 최근날짜부터 INSERT 이므로 일배치 시작날짜 이전데이터를 가져올 경우는 없다.
                scan_date = event_status.first()[0]
            else:  # init 배치를 실행하지 않고 daily 배치만 실행하는경우 최근 일주일간 데이터를 가져오기.
                scan_date = (today_org - datetime.timedelta(days=8)).date()

            # 하루단위 전체종목 insert
            while scan_date < today_org.date():  # 날짜별 insert
                scan_date += datetime.timedelta(days=1)
                scan_date_str = scan_date.strftime('%Y%m%d')
                logger.info(
                    '{}index price INSERT. market = {}, date = {}'.format(logger_method, market, scan_date_str))
                info_df = None
                try:
                    info_df = stock.get_index_ohlcv_by_ticker(scan_date_str, market)
                except Exception as e:
                    logger.error(
                        '{}get price data error. date={}, error message={}'.format(logger_method, scan_date_str,
                                                                                   e))
                if info_df is None or len(info_df) == 0:
                    logger.error('{}get empty data. date={} skip.'.format(logger_method, scan_date_str))
                    continue

                holiday = (info_df[['시가', '고가', '저가', '종가']] == 0).all(
                    axis=None)
                if holiday:
                    continue

                info_df = info_df.replace({np.nan: None})
                # info_df = info_df[['보유수량', '지분율', '한도수량', '한도소진률']]
                info_df.rename(
                    columns={'시가': 'open', '종가': 'close', '거래량': 'volume', '고가': 'high',
                             '저가': 'low', '거래대금': 'value', '등락률': 'up_down_rate',
                             '등락유형': 'up_down_sort', '등락폭': 'up_down_value', '상장시가총액': 'market_cap'},
                    inplace=True)
                info_df['date'] = scan_date
                with transaction.atomic():
                    for k, v in info_df.to_dict('index').items():
                        # 특정 코드 테스트 시 사용
                        # if BATCH_INDEX_TEST_CODE_YN:
                        #     if k not in BATCH_INDEX_TEST_CODE_LIST:
                        #         continue
                        pattern = r'[^a-zA-Z0-9가-힣]'
                        # 특수문자를 공백으로 치환
                        market_index_dense_nm = re.sub(pattern, '', k)

                        if market_index_dense_nm == '코스닥지수':
                            market_index_dense_nm = '코스닥'

                        index_info = IndexBasicInfo.objects.filter(index_dense_nm=market_index_dense_nm).filter(
                            mkt_code=krxIndexMarketCode(market))
                        if index_info.count() == 0:  # 정보는 존재하나 krx 종목정보에 등록되어 있지 않은 경우 UPDATE 취소
                            # logger.error('{}KRX 종목 정보에 등록되어 있지 않음. code = {}'.format(logger_method, k))
                            continue

                        entry = IndexPriceInfo(**v)
                        entry.stock_index_id = index_info.first().stock_index_id
                        entry.save()

                    # 시장종류별로 최신일 status 업데이트.
                    event_status = InfoUpdateStatus.objects.filter(table_type=dbTableType('지수가')).filter(
                        class_id=krxIndexMarketCode(market))
                    if len(event_status) == 0:
                        status_dict = {'table_type': dbTableType('지수가'), 'mod_dt': scan_date,
                                       'reg_dt': scan_date,
                                       'update_type': 'U', 'class_id': krxIndexMarketCode(market)}
                        event_status_insert = InfoUpdateStatus(**status_dict)
                        event_status_insert.save()
                    else:
                        event_status.update(mod_dt=scan_date)

        logger.info('{}end'.format(logger_method))

    except Exception as e:
        logger.exception('{}error occured'.format(logger_method))


# 시가총액과 상장주식수에 대해 종목별 UPDATE
def manage_event_init_etc():
    logger_method = '[manage_event_init_etc] '
    try:
        global first
        global etc_first
        #
        while first:
            time.sleep(10)
            logger.info('{}waiting for manage_event_init to compelete'.format(logger_method))
        if not first:
            logger.info('{}start'.format(logger_method))
            todate = FIRST_BATCH_TODATE
            todate_org = datetime.datetime.strptime(todate, '%Y%m%d')
            etc_first = True
            cur_event_info = EventInfo.objects.all()
            for cur_event in cur_event_info:
                if BATCH_TEST_CODE_YN:
                    if cur_event.event_code not in BATCH_TEST_CODE_LIST:
                        continue
                # 기존 등록된 종목인지 확인.
                event_status = InfoUpdateStatus.objects.filter(class_id=cur_event.stock_event_id) \
                    .filter(table_type=dbTableType('종목미수정종가'))
                if event_status.count() != 0:  # 이미 등록된 것이면 스킵.
                    logger.info('{}{} already inserted. skip inserting.'.format(logger_method, cur_event.event_code))
                    continue
                else:  # 종목정보 INSERT 중, 비정상종료된 케이스로 간주하고 해당 종목정보들 삭제 후 재등록
                    logger.info(
                        '{}{} incompleted or not inserted. delete and re-insert.'.format(logger_method,
                                                                                         cur_event.event_code))
                    not_adj_price = NotAdjPriceInfo.objects.filter(stock_event_id=cur_event.stock_event_id)
                    if not_adj_price.count() != 0:
                        not_adj_price.delete()

                # price_info 테이블에서 주가 시작날짜 조회
                start_price_info = PriceInfo.objects.filter(
                    stock_event_id=cur_event.stock_event_id).order_by('date')[:1]
                fromdate = start_price_info.first().date.strftime('%Y%m%d')
                not_adj_price_info = stock_custom.get_market_ohlcv_by_date(fromdate=fromdate, todate=todate,
                                                                           ticker=cur_event.event_code)
                if len(not_adj_price_info) == 0:
                    continue

                not_adj_price_info = not_adj_price_info.replace({np.nan: None})

                not_adj_price_info = not_adj_price_info.reset_index()
                not_adj_price_info.rename(
                    columns={'날짜': 'date', '시가': 'open', '종가': 'close',
                             '거래량': 'volume', '고가': 'high', '저가': 'low',
                             '거래대금': 'value', '등락률': 'up_down_rate',
                             '등락유형': 'up_down_sort', '등락폭': 'up_down_value',
                             '시가총액': 'market_cap', '상장주식수': 'listed_shares'},
                    inplace=True)
                # stockprice 테이블에 insert
                with transaction.atomic():
                    for price_item in not_adj_price_info.to_dict('records'):
                        if price_item['open'] != 0 and price_item['high'] != 0 \
                                and price_item['low'] != 0 and price_item['close'] != 0:
                            entry = NotAdjPriceInfo(**price_item)
                            entry.stock_event_id = cur_event.stock_event_id
                            entry.save()

                status_dict = {'table_type': dbTableType('종목미수정종가'), 'mod_dt': todate_org, 'reg_dt': todate_org,
                               'update_type': 'U', 'class_id': cur_event.stock_event_id}
                event_status_insert = InfoUpdateStatus(**status_dict)
                event_status_insert.save()
        else:
            logger.info('{}manage_event_init executed. skip init_etc'.format(logger_method))

    except Exception as e:
        logger.exception('{}error occured'.format(logger_method))
    finally:
        etc_first = False


def manage_event_daily_etc():
    global first
    # global etc_first
    logger_method = '[manage_event_daily_etc] '
    if not first:
        logger.info('{}start'.format(logger_method))
        today_org = datetime.datetime.now()
        today = today_org.strftime('%Y%m%d')

        cur_event_info = EventInfo.objects.all()
        cur_event_info_list = []
        for cur_event in cur_event_info:
            cur_event_info_list.append(cur_event.stock_event_id)

        not_adj_event_id_list = NotAdjPriceInfo.objects.distinct().values_list('stock_event_id')
        for not_adj_event_tuple in not_adj_event_id_list:
            not_adj_event_id = not_adj_event_tuple[0]  # distinct를 이용하면 결과값이 tuple이 된다. 그중 처음값 이용.
            if not_adj_event_id not in cur_event_info_list:
                # 현재 DB 종목리스트에 등록되어있는 종목이 아니라면 삭제하기
                not_adj_delete_event = NotAdjPriceInfo.objects.filter(stock_event_id=not_adj_event_id)
                not_adj_delete_event.delete()
                continue

        # # 가장 오래된 일괄처리 처리 날짜 조회하여 해당날짜 이후부터 INSERT (누락건에 대해 체크)
        # # mod_dt를 오름차순으로 정렬
        # event_status = InfoUpdateStatus.objects.filter(table_type=dbTableType('종목미수정종가')).distinct().values_list('mod_dt').order_by(
        #     'mod_dt')[:1]

        # scan_date = None
        # if event_status.count() != 0 and not :
        #     # 안정성을 위해 해당날짜 이후 데이터 일괄 삭제 후 RE-INSERT
        #     not_adj_delete_by_date = NotAdjPriceInfo.objects.filter(
        #         date__range=[event_status.first()[0] + datetime.timedelta(days=1), today_org])
        #     not_adj_delete_by_date.delete()
        #     scan_date = event_status.first()[0]
        # else:  # init 배치를 실행하지 않고 daily 배치만 실행하는경우 오늘날짜부터 insert

        # # 가장 최근의 일괄처리 처리 날짜 조회하여 해당날짜 이후부터 INSERT (누락건에 대해 체크)
        # mod_dt를 내림차순으로 정렬
        event_status = InfoUpdateStatus.objects.filter(table_type=dbTableType('종목미수정종가')).distinct().values_list(
            'mod_dt').order_by(
            '-mod_dt')[:1]

        scan_date = None
        if event_status.count() != 0:  # 최근날짜부터 INSERT 이므로 일배치 시작날짜 이전데이터를 가져올 경우는 없다.
            # # 안정성을 위해 해당날짜 이후 데이터 일괄 삭제 후 RE-INSERT
            # not_adj_delete_by_date = NotAdjPriceInfo.objects.filter(
            #     date__range=[event_status.first()[0] + datetime.timedelta(days=1), today_org])
            # not_adj_delete_by_date.delete()
            scan_date = event_status.first()[0]
        else:  # init 배치를 실행하지 않고 daily 배치만 실행하는경우 오늘날짜부터 insert
            scan_date = (today_org - datetime.timedelta(days=1)).date()
        while scan_date != today_org.date():  # 날짜별 INSERT
            scan_date += datetime.timedelta(days=1)
            scan_date_str = scan_date.strftime('%Y%m%d')
            not_adj_price_info = stock_custom.get_market_ohlcv_by_ticker(date=scan_date_str, market="ALL")
            holiday = (not_adj_price_info[['시가', '고가', '저가', '종가']] == 0).all(axis=None)
            if holiday:
                continue

            not_adj_price_info = not_adj_price_info.replace({np.nan: None})
            # not_adj_price_info = not_adj_price_info[['티커', '시가', '고가', '저가', '종가', '거래량', '거래대금',
            #                                          '등락률', '등락유형', '등락폭', '시가총액', '상장주식수']]
            not_adj_price_info.rename(
                columns={'시가': 'open', '종가': 'close', '거래량': 'volume', '고가': 'high',
                         '저가': 'low', '거래대금': 'value', '등락률': 'up_down_rate',
                         '등락유형': 'up_down_sort', '등락폭': 'up_down_value', '시장': 'mkt_code',
                         '시가총액': 'market_cap', '상장주식수': 'listed_shares'}, inplace=True)
            not_adj_price_info['date'] = scan_date

            with transaction.atomic():
                for k, v in not_adj_price_info.to_dict('index').items():
                    if BATCH_TEST_CODE_YN:
                        if k not in BATCH_TEST_CODE_LIST:
                            continue

                    event_info = EventInfo.objects.filter(event_code=k)

                    if event_info.count() == 0 or event_info.first() is None:  # 가격정보는 존재하나 krx 종목정보에 등록되어 있지 않은 경우 SKIP
                        # logger.error('{}eventinfo에 등록되어 있지 않음. code = {}'.format(logger_method, k))
                        continue
                    # else:
                    #     # 종목정보에 등록도 되어있으나, 미수정종가테이블에 아예 INSERT가 되지 않았다면 SKIP
                    #     # 이전가격정보가 없으면 insert 하지 않는 로직이었지만, daily batch가 독립화되면 필요없음.
                    #     before_not_adj_price_info = NotAdjPriceInfo.objects.filter(
                    #         stock_event_id=event_info.first().stock_event_id)
                    #     if before_not_adj_price_info.count() == 0:
                    #         continue

                    # mkt_code 은 eventinfo 테이블에 넣기 위한 정보이므로 priceinfo 테이블에 넣기전에 빼기.
                    event_mkt_code = None
                    if v['mkt_code'] == 'KOSPI':
                        event_mkt_code = krxMarketCode('KOSPI')
                    elif v['mkt_code'] == 'KOSDAQ' or v['mkt_code'] == 'KOSDAQGLOBAL':
                        event_mkt_code = krxMarketCode('KOSDAQ')
                    elif v['mkt_code'] == 'KONEX':
                        event_mkt_code = krxMarketCode('KONEX')
                    v.pop('mkt_code')

                    if v['open'] != 0 and v['high'] != 0 and v['low'] != 0 and v['close'] != 0:
                        # logger.info('{}금일 주가 INSERT : code={}'.format(logger_method, k))
                        entry = NotAdjPriceInfo(**v)
                        entry.stock_event_id = event_info.first().stock_event_id
                        entry.save()
                        # print(event_info.first())
                        # print(event_info.first().mkt_status)
                        if event_info.first().mkt_status is None or event_info.first().mkt_status != krxMarketStatusCode(
                                '정상'):
                            event_info.update(mkt_status=krxMarketStatusCode('정상'))
                    elif v['open'] == 0 and v['high'] == 0 and v['low'] == 0 and v['close'] != 0:  # 거래정지 태그 업데이트
                        if event_info.first().mkt_status is None or event_info.first().mkt_status != krxMarketStatusCode(
                                '거래정지'):
                            event_info.update(mkt_status=krxMarketStatusCode('거래정지'))
                    else:
                        if event_info.first().mkt_status is None or event_info.first().mkt_status != krxMarketStatusCode(
                                '전산오류'):
                            event_info.update(mkt_status=krxMarketStatusCode('전산오류'))

                    # 시장명 다르거나 없다면 업데이트
                    if event_info.first().mkt_code is None or event_info.first().mkt_code != event_mkt_code:
                        event_info.update(mkt_code=event_mkt_code)

                event_status = InfoUpdateStatus.objects.filter(table_type=dbTableType('종목미수정종가'))
                if len(event_status) == 0:
                    status_dict = {'table_type': dbTableType('종목미수정종가'), 'mod_dt': scan_date, 'reg_dt': scan_date,
                                   'update_type': 'U'}
                    event_status_insert = InfoUpdateStatus(**status_dict)
                    event_status_insert.save()
                else:
                    event_status.update(mod_dt=scan_date)

    else:
        logger.info('{}manage_event_init executed. skip daily_etc'.format(logger_method))

    logger.info('{}end'.format(logger_method))


# def manage_fundamental():
#     logger_method = '[manage_fundamental] '
#     logger.info('{}start'.format(logger_method))
#
#     while first:
#         time.sleep(10)
#         logger.info('{}waiting for manage_event_init to compelete'.format(logger_method))
#     if not first:
#         cur_datetime = datetime.datetime.now()
#         cur_date_str = cur_datetime.strftime('%Y%m%d')
#         cur_qt = calcQuarter(cur_datetime)
#         # cur_year = cur_datetime.strftime('%Y')
#
#         all_event_info = EventInfo.objects.all()
#         cur_event_id_list = []
#         for cur_event in all_event_info:
#             cur_event_id_list.append(cur_event.stock_event_id)
#
#         fund_event_id_list = FinancialStatement.objects.distinct().values_list('stock_event_id')
#         for fund_event_tuple in fund_event_id_list:
#             fund_event_id = fund_event_tuple[0]  # distinct를 이용하면 결과값이 tuple이 된다. 그중 처음값 이용.
#             if fund_event_id not in cur_event_id_list:
#                 # 현재 DB 종목리스트에 등록되어있는 종목이 아니라면 삭제하기
#                 fund_delete_event = FinancialStatement.objects.filter(stock_event_id=fund_event_id)
#                 fund_delete_event.delete()
#                 continue
#
#         shares_id_list = StockShares.objects.distinct().values_list('stock_event_id')
#         for shares_tuple in shares_id_list:
#             shares_id = shares_tuple[0]  # distinct를 이용하면 결과값이 tuple이 된다. 그중 처음값 이용.
#             if shares_id not in cur_event_id_list:
#                 # 현재 DB 종목리스트에 등록되어있는 종목이 아니라면 삭제하기
#                 delete_list = StockShares.objects.filter(stock_event_id=shares_id)
#                 delete_list.delete()
#                 continue
#
#         STOP_FINSTATE_TF = False  # 예외상황이 발생하였을때, 작업중지플래그
#
#         if not FUND_SKIP_FINSTATE:
#             STOP_FINSTATE_TF = manage_finstate(STOP_FINSTATE_TF, all_event_info, cur_qt)
#
#         if STOP_FINSTATE_TF:
#             logger.error('{}stop because of finstate error')
#             return
#
#         STOP_SHARES_TF = False
#         if not FUND_SKIP_CO:
#             STOP_SHARES_TF = manage_stockshares(STOP_SHARES_TF, all_event_info, cur_qt)
#
#         if STOP_SHARES_TF:
#             logger.error('{}stop because of shares error')
#             return
#
#         # 정상적으로 배치가 끝난다면 리트라이 플래그 False로 변경
#         if not STOP_FINSTATE_TF:
#             StockBatchManager.instance().set_retry_fund(False)
#         if not STOP_SHARES_TF:
#             StockBatchManager.instance().set_retry_shares(False)
#
#         logger.info('{}end'.format(logger_method))
#
#
# def manage_finstate(STOP_FUND_TF, all_event_info, cur_qt):
#     logger_method = '[manage_finstate] '
#     try:
#         finstate_skip_qryset = FinancialStatementSkip.objects.all()
#         finstate_skip_list = []
#         for finstate_skip in finstate_skip_qryset:
#             finstate_skip_list.append(
#                 {'stock_event_id': finstate_skip.stock_event_id, 'quarter': finstate_skip.quarter})
#
#         for event_info in all_event_info:
#             if STOP_FUND_TF:
#                 logger.error('{}stop batch because of error'.format(logger_method))
#                 break
#             if BATCH_TEST_CODE_YN:
#                 if event_info.event_code not in BATCH_TEST_CODE_LIST:
#                     continue
#                 else:
#                     logger.info('TEST : {}/{}'.format(event_info.event_code, event_info.event_name))
#             # fundamental table에서 현재종목의 가장 최근 분기 가져오기.
#             recent_quarter = FinancialStatement.objects.filter(stock_event_id=event_info.stock_event_id).order_by(
#                 '-quarter')[:1]
#
#             scan_qt = None
#             if recent_quarter.count() == 0:  # 등록된 재무정보가 아예없을경우
#                 # 가격정보에서 조회한 주가시작날짜를 첫번쨰 조회분기로 지정
#                 start_price_info = PriceInfo.objects.filter(
#                     stock_event_id=event_info.stock_event_id).order_by('date')[:1]
#                 # 신규상장종목의 경우 종목정보에는 들어가는데 가격정보에는 없을수 있다.
#                 # 이때는 당연히 아직 재무정보공시가 아직 안된 시점이므로 이점 참고하여 예외처리.
#                 if start_price_info is None or start_price_info.first() is None:
#                     continue
#                 else:
#                     scan_qt = calcQuarter(start_price_info.first().date)
#             else:
#                 scan_qt = calcNextQuarter(recent_quarter.first().quarter)
#
#             # 조회한 시작분기가 2015년 1분기보다 더 오래되었을때 최소조회분기를 2015년 1분기로 지정
#             # min_qt = calcFirstQuarterOfMinYear(cur_datetime)
#             min_qt = '201503'
#             if min_qt > scan_qt:
#                 scan_qt = min_qt
#
#             while cur_qt > scan_qt:
#                 logger.info('{}event = {}/{}/{}, scan_qt={}'.format(logger_method, event_info.stock_event_id,
#                                                                     event_info.event_name, event_info.event_code,
#                                                                     scan_qt))
#                 if {'stock_event_id': event_info.stock_event_id, 'quarter': scan_qt} in finstate_skip_list:
#                     logger.info('{}Register in finstate_skip table. skip.'.format(logger_method))
#                     # 다음 분기 계산
#                     scan_qt = calcNextQuarter(scan_qt)
#                     continue
#                 scan_date = datetime.datetime.strptime(scan_qt, '%Y%m')
#                 quarter_code = calcQuarterCode(scan_date)
#
#                 # 해당년도의 첫번째분기가 DB에 등록되어있지 않다면 다음년도로 넘어가기.
#                 if not scan_qt.endswith('03'):
#                     is_valid = validateQuarter(qt=scan_qt, stock_event_id=event_info.stock_event_id)
#                     if not is_valid:
#                         scan_qt = calcFirstQuarterOfNextYear(scan_qt)
#                         continue
#                 finstate = None
#                 try:
#                     finstate = DartManager.instance().get_dart().finstate_all(event_info.event_code, scan_date.year,
#                                                                               quarter_code)
#                 except Exception as e:
#                     if isinstance(e, ValueError) and isinstance(e.args, tuple):
#                         if isinstance(e.args[0], str) and e.args[0].startswith('could not find'):
#                             logger.error('could not find corps code {}. skip.'.format(event_info.event_name))
#                             # 조회된 데이터가 없을 경우 나중에도 스킵할수 있도록 DB 등록.
#                             includeYn = isIncludeRecent3Qt(cur_qt, scan_qt)
#                             if not includeYn:
#                                 logger.error('Searched corp code is None. register skip list to db.')
#                                 entry = FinancialStatementSkip(
#                                     **{'stock_event_id': event_info.stock_event_id, 'quarter': scan_qt,
#                                        'skip_yn': 'Y',
#                                        })
#                                 entry.save()
#                         elif isinstance(e.args[0], dict) and 'status' in e.args[0]:
#                             if e.args[0]['status'] == '020' or e.args[0]['status'] == '800' or e.args[0][
#                                 'status'] == '901':
#                                 STOP_FUND_TF = True
#                                 StockBatchManager.instance().set_retry_fund(False)
#                                 break
#                             elif e.args[0]['status'] == '013':
#                                 # 조회된 데이터가 없을 경우 나중에도 스킵할수 있도록 DB 등록.
#                                 includeYn = isIncludeRecent3Qt(cur_qt, scan_qt)
#                                 if not includeYn:
#                                     logger.error('Searched finstate data is None. register skip list to db.')
#                                     entry = FinancialStatementSkip(
#                                         **{'stock_event_id': event_info.stock_event_id, 'quarter': scan_qt,
#                                            'skip_yn': 'Y',
#                                            })
#                                     entry.save()
#
#                     else:
#                         logger.exception('get request error')
#                         STOP_FUND_TF = True
#                         StockBatchManager.instance().set_retry_fund(True)
#                         break
#                 # logger.info('finstate = {}'.format(finstate))
#                 if finstate is not None:
#                     try:
#                         assets = 0
#                         current_assets = 0
#                         non_current_assets = 0
#                         liabilities = 0
#                         current_liabilities = 0
#                         non_current_liabilities = 0
#                         equity = 0
#                         equity_control = 0
#                         equity_non_control = 0
#                         revenue = 0
#                         cost_of_sales = 0
#                         gross_profit = 0
#                         operating_income_loss = 0
#                         profit_loss = 0
#                         profit_loss_control = 0
#                         profit_loss_non_control = 0
#                         profit_loss_before_tax = 0
#                         investing_cash_flow = 0
#                         operating_cash_flow = 0
#                         financing_cash_flow = 0
#                         try:
#                             assets_org = finstate.loc[DartFinstateConfig().assets_condition(finstate)].iloc[0][
#                                 DartFinstateConfig().column_amount]
#                             assets = 0 if assets_org == '' else int(assets_org)
#                         except Exception as e:
#                             logger.error('{}assets error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                 logger_method, event_info.event_name, event_info.event_code, scan_qt))
#                         try:
#                             current_assets_org = \
#                                 finstate.loc[DartFinstateConfig().current_assets_condition(finstate)].iloc[0][
#                                     DartFinstateConfig().column_amount]
#                             current_assets = 0 if current_assets_org == '' else int(current_assets_org)
#                         except Exception as e:
#                             logger.error(
#                                 '{}current_assets error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                     logger_method, event_info.event_name, event_info.event_code, scan_qt))
#                         try:
#                             non_current_assets_org = \
#                                 finstate.loc[DartFinstateConfig().non_current_assets_condition(finstate)].iloc[0][
#                                     DartFinstateConfig().column_amount]
#                             non_current_assets = 0 if non_current_assets_org == '' else int(non_current_assets_org)
#                         except Exception as e:
#                             logger.error(
#                                 '{}non_current_assets error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                     logger_method, event_info.event_name, event_info.event_code, scan_qt))
#                         try:
#                             liabilities_org = \
#                                 finstate.loc[DartFinstateConfig().liabilities_condition(finstate)].iloc[0][
#                                     DartFinstateConfig().column_amount]
#                             liabilities = 0 if liabilities_org == '' else int(liabilities_org)
#                         except Exception as e:
#                             logger.error(
#                                 '{}liabilities error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                     logger_method, event_info.event_name, event_info.event_code, scan_qt))
#                         try:
#                             current_liabilities_org = \
#                                 finstate.loc[DartFinstateConfig().current_liabilities_condition(finstate)].iloc[0][
#                                     DartFinstateConfig().column_amount]
#                             current_liabilities = 0 if current_liabilities_org == '' else int(
#                                 current_liabilities_org)
#                         except Exception as e:
#                             logger.error(
#                                 '{}current_liabilities error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                     logger_method, event_info.event_name, event_info.event_code, scan_qt))
#
#                         try:
#                             non_current_liabilities_org = \
#                                 finstate.loc[DartFinstateConfig().non_current_liabilities_condition(finstate)].iloc[
#                                     0][
#                                     DartFinstateConfig().column_amount]
#                             non_current_liabilities = 0 if non_current_liabilities_org == '' else int(
#                                 non_current_liabilities_org)
#                         except Exception as e:
#                             logger.error(
#                                 '{}non_current_liabilities error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                     logger_method, event_info.event_name, event_info.event_code, scan_qt))
#
#                         try:
#                             equity_org = finstate.loc[DartFinstateConfig().equity_condition(finstate)].iloc[0][
#                                 DartFinstateConfig().column_amount]
#                             equity = 0 if equity_org == '' else int(equity_org)
#                         except Exception as e:
#                             logger.error('{}equity error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                 logger_method, event_info.event_name, event_info.event_code, scan_qt))
#                         try:
#                             equity_control_org = \
#                                 finstate.loc[DartFinstateConfig().equity_control_condition(finstate)].iloc[0][
#                                     DartFinstateConfig().column_amount]
#                             equity_control = 0 if equity_control_org == '' else int(equity_control_org)
#                         except Exception as e:
#                             logger.error(
#                                 '{}equity_control error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                     logger_method, event_info.event_name, event_info.event_code, scan_qt))
#                         try:
#                             equity_non_control_org = \
#                                 finstate.loc[DartFinstateConfig().equity_non_control_condition(finstate)].iloc[0][
#                                     DartFinstateConfig().column_amount]
#                             equity_non_control = 0 if equity_non_control_org == '' else int(equity_non_control_org)
#                         except Exception as e:
#                             logger.error(
#                                 '{}equity_non_control error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                     logger_method, event_info.event_name, event_info.event_code, scan_qt))
#                         try:
#                             revenue_org = finstate.loc[DartFinstateConfig().revenue_condition(finstate)].iloc[0][
#                                 DartFinstateConfig().column_amount]
#                             revenue = 0 if revenue_org == '' else int(revenue_org)
#                         except Exception as e:
#                             logger.error('{}revenue error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                 logger_method, event_info.event_name, event_info.event_code, scan_qt))
#                         try:
#                             cost_of_sales_org = \
#                                 finstate.loc[DartFinstateConfig().cost_of_sales_condition(finstate)].iloc[0][
#                                     DartFinstateConfig().column_amount]
#                             cost_of_sales = 0 if cost_of_sales_org == '' else int(cost_of_sales_org)
#                         except Exception as e:
#                             logger.error(
#                                 '{}cost_of_sales error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                     logger_method, event_info.event_name, event_info.event_code, scan_qt))
#
#                         try:
#                             gross_profit_org = \
#                                 finstate.loc[DartFinstateConfig().gross_profit_condition(finstate)].iloc[0][
#                                     DartFinstateConfig().column_amount]
#                             gross_profit = 0 if gross_profit_org == '' else int(gross_profit_org)
#                         except Exception as e:
#                             logger.error(
#                                 '{}gross_profit error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                     logger_method, event_info.event_name, event_info.event_code, scan_qt))
#                         try:
#                             operating_income_loss_org = \
#                                 finstate.loc[DartFinstateConfig().operating_income_loss_condition(finstate)].iloc[
#                                     0][
#                                     DartFinstateConfig().column_amount]
#                             operating_income_loss = 0 if operating_income_loss_org == '' else int(
#                                 operating_income_loss_org)
#                         except Exception as e:
#                             logger.error(
#                                 '{}operating_income_loss error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                     logger_method, event_info.event_name, event_info.event_code, scan_qt))
#                         try:
#                             profit_loss_org = \
#                                 finstate.loc[DartFinstateConfig().profit_loss_condition(finstate)].iloc[0][
#                                     DartFinstateConfig().column_amount]
#                             profit_loss = 0 if profit_loss_org == '' else int(profit_loss_org)
#                         except Exception as e:
#                             logger.error(
#                                 '{}profit_loss error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                     logger_method, event_info.event_name, event_info.event_code, scan_qt))
#                         try:
#                             profit_loss_control_org = \
#                                 finstate.loc[DartFinstateConfig().profit_loss_control_condition(finstate)].iloc[0][
#                                     DartFinstateConfig().column_amount]
#                             profit_loss_control = 0 if profit_loss_control_org == '' else int(
#                                 profit_loss_control_org)
#                         except Exception as e:
#                             logger.error(
#                                 '{}profit_loss_control error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                     logger_method, event_info.event_name, event_info.event_code, scan_qt))
#                         try:
#                             profit_loss_non_control_org = \
#                                 finstate.loc[DartFinstateConfig().profit_loss_non_control_condition(finstate)].iloc[
#                                     0][
#                                     DartFinstateConfig().column_amount]
#                             profit_loss_non_control = 0 if profit_loss_non_control_org == '' else int(
#                                 profit_loss_non_control_org)
#                         except Exception as e:
#                             logger.error(
#                                 '{}profit_loss_non_control error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                     logger_method, event_info.event_name, event_info.event_code, scan_qt))
#                         try:
#                             profit_loss_before_tax_org = \
#                                 finstate.loc[DartFinstateConfig().profit_loss_before_tax_condition(finstate)].iloc[
#                                     0][
#                                     DartFinstateConfig().column_amount]
#                             profit_loss_before_tax = 0 if profit_loss_before_tax_org == '' else int(
#                                 profit_loss_before_tax_org)
#                         except Exception as e:
#                             logger.error(
#                                 '{}profit_loss_before_tax error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                     logger_method, event_info.event_name, event_info.event_code, scan_qt))
#
#                         # eps = int(
#                         #     finstate.loc[DartFinstateConfig().eps_condition(finstate)].iloc[0][DartFinstateConfig().column_amount])
#                         try:
#                             investing_cash_flow_org = \
#                                 finstate.loc[DartFinstateConfig().investing_cash_flow_condition(finstate)].iloc[0][
#                                     DartFinstateConfig().column_amount]
#                             investing_cash_flow = 0 if investing_cash_flow_org == '' else int(
#                                 investing_cash_flow_org)
#                         except Exception as e:
#                             logger.error(
#                                 '{}liabilities error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                     logger_method, event_info.event_name, event_info.event_code, scan_qt))
#                         try:
#                             operating_cash_flow_org = \
#                                 finstate.loc[DartFinstateConfig().operating_cash_flow_condition(finstate)].iloc[0][
#                                     DartFinstateConfig().column_amount]
#                             operating_cash_flow = 0 if operating_cash_flow_org == '' else int(
#                                 operating_cash_flow_org)
#                         except Exception as e:
#                             logger.error(
#                                 '{}liabilities error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                     logger_method, event_info.event_name, event_info.event_code, scan_qt))
#                         try:
#                             financing_cash_flow_org = \
#                                 finstate.loc[DartFinstateConfig().financing_cash_flow_condition(finstate)].iloc[0][
#                                     DartFinstateConfig().column_amount]
#                             financing_cash_flow = 0 if financing_cash_flow_org == '' else int(
#                                 financing_cash_flow_org)
#                         except Exception as e:
#                             logger.error(
#                                 '{}liabilities error. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                     logger_method, event_info.event_name, event_info.event_code, scan_qt))
#
#                         recent_quarter = FinancialStatement.objects.filter(
#                             stock_event_id=event_info.stock_event_id) \
#                             .filter(quarter__startswith=str(scan_date.year))
#                         # logger.info('{}get recent qt count={}'.format(logger_method, recent_quarter.count()))
#                         if quarter_code == '11011':  # 사업보고서의 경우 1,2,3분기를 합산한 금액을 감액해야 4분기 계산가능
#                             for item in recent_quarter:
#                                 if not item.quarter.endswith('12'):
#                                     # if revenue is not None:
#                                     revenue -= item.revenue
#                                     # if cost_of_sales is not None:
#                                     cost_of_sales -= item.cost_of_sales
#                                     # if gross_profit is not None:
#                                     gross_profit -= item.gross_profit
#                                     # if operating_income_loss is not None:
#                                     operating_income_loss -= item.operating_income_loss
#                                     # if profit_loss is not None:
#                                     profit_loss -= item.profit_loss
#                                     # if profit_loss_control is not None:
#                                     profit_loss_control -= item.profit_loss_control
#                                     # if profit_loss_non_control is not None:
#                                     profit_loss_non_control -= item.profit_loss_non_control
#                                     # if profit_loss_before_tax is not None:
#                                     profit_loss_before_tax -= item.profit_loss_before_tax
#                                     # eps -= item.eps
#                                     # if investing_cash_flow is not None:
#                                     investing_cash_flow -= item.investing_cash_flow
#                                     # if operating_cash_flow is not None:
#                                     operating_cash_flow -= item.operating_cash_flow
#                                     # if financing_cash_flow is not None:
#                                     financing_cash_flow -= item.financing_cash_flow
#
#                         if quarter_code == '11012':  # 2분기 현금흐름 계산
#                             for item in recent_quarter:
#                                 if item.quarter.endswith('03'):
#                                     # if investing_cash_flow is not None:
#                                     investing_cash_flow -= item.investing_cash_flow
#                                     # if operating_cash_flow is not None:
#                                     operating_cash_flow -= item.operating_cash_flow
#                                     # if financing_cash_flow is not None:
#                                     financing_cash_flow -= item.financing_cash_flow
#
#                         if quarter_code == '11014':  # 3분기 현금흐름 계산
#                             for item in recent_quarter:
#                                 if item.quarter.endswith('03') or item.quarter.endswith('06'):
#                                     # if investing_cash_flow is not None:
#                                     investing_cash_flow -= item.investing_cash_flow
#                                     # if operating_cash_flow is not None:
#                                     operating_cash_flow -= item.operating_cash_flow
#                                     # if financing_cash_flow is not None:
#                                     financing_cash_flow -= item.financing_cash_flow
#
#                         entry = FinancialStatement(
#                             **{'stock_event_id': event_info.stock_event_id, 'quarter': scan_qt,
#                                'assets': assets, 'current_assets': current_assets,
#                                'non_current_assets': non_current_assets,
#                                'liabilities': liabilities, 'current_liabilities': current_liabilities,
#                                'non_current_liabilities': non_current_liabilities,
#                                'equity': equity, 'equity_control': equity_control,
#                                'equity_non_control': equity_non_control,
#                                'revenue': revenue, 'cost_of_sales': cost_of_sales,
#                                'gross_profit': gross_profit,
#                                'operating_income_loss': operating_income_loss,
#                                'profit_loss': profit_loss, 'profit_loss_control': profit_loss_control,
#                                'profit_loss_non_control': profit_loss_non_control,
#                                'profit_loss_before_tax': profit_loss_before_tax,
#                                # 'eps': eps,
#                                'investing_cash_flow': investing_cash_flow,
#                                'operating_cash_flow': operating_cash_flow,
#                                'financing_cash_flow': financing_cash_flow})
#                         entry.save()
#                     except Exception as e:
#                         logger.exception(
#                             '{}error occured. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                 logger_method, event_info.event_name, event_info.event_code, scan_qt))
#
#                 # 다음 분기 계산
#                 scan_qt = calcNextQuarter(scan_qt)
#                 time.sleep(FUND_API_REQUEST_TERM)
#
#     except Exception as e:
#         STOP_FUND_TF = True
#         StockBatchManager.instance().set_retry_fund(False)
#         logger.exception('{} error occured. stop request')
#     return STOP_FUND_TF
#
#
# def manage_stockshares(STOP_SHARES_TF, all_event_info, cur_qt):
#     logger_method = '[manage_stockshares] '
#     try:
#         shares_retry_recent_id = 0
#         if StockBatchManager.instance().is_retry_fund():
#             shares_retry_recent_id = StockShares.objects.order_by('-stock_event_id')[:1].first().stock_event_id
#             logger.info('{}RETRY. get recent stock_event_id in shares table. stock_event_id = {}'.format(
#                 logger_method, shares_retry_recent_id))
#
#         for event_info in all_event_info:
#             if STOP_SHARES_TF:
#                 logger.error('{}stop batch because of error'.format(logger_method))
#                 break
#             if shares_retry_recent_id > event_info.stock_event_id:
#                 logger.info('{}skip stock_event_id = {}'.format(logger_method, event_info.stock_event_id))
#                 continue
#             if BATCH_TEST_CODE_YN:
#                 if event_info.event_code not in BATCH_TEST_CODE_LIST:
#                     continue
#                 else:
#                     logger.info('TEST : {}/{}'.format(event_info.event_code, event_info.event_name))
#             # fundamental table에서 현재종목의 가장 최근 분기 가져오기.
#             recent_quarter = StockShares.objects.filter(stock_event_id=event_info.stock_event_id).order_by(
#                 '-quarter')[:1]
#
#             scan_qt = None
#             if recent_quarter.count() == 0:  # 등록된 재무정보가 아예없을경우
#                 # 가격정보에서 조회한 주가시작날짜를 첫번쨰 조회분기로 지정
#                 start_price_info = PriceInfo.objects.filter(
#                     stock_event_id=event_info.stock_event_id).order_by('date')[:1]
#                 # 신규상장종목의 경우 종목정보에는 들어가는데 가격정보에는 없을수 있다.
#                 # 이때는 당연히 아직 재무정보공시가 아직 안된 시점이므로 이점 참고하여 예외처리.
#                 if start_price_info is None or start_price_info.first() is None:
#                     continue
#                 else:
#                     scan_qt = calcQuarter(start_price_info.first().date)
#             else:
#                 scan_qt = calcNextQuarter(recent_quarter.first().quarter)
#
#             # 조회한 시작분기가 2015년 1분기보다 더 오래되었을때 최소조회분기를 2015년 1분기로 지정
#             # min_qt = calcFirstQuarterOfMinYear(cur_datetime)
#             min_qt = '201503'
#             if min_qt > scan_qt:
#                 scan_qt = min_qt
#
#             while cur_qt > scan_qt:
#                 logger.info('{}event = {}/{}/{}, scan_qt={}'.format(logger_method, event_info.stock_event_id,
#                                                                     event_info.event_name, event_info.event_code,
#                                                                     scan_qt))
#                 scan_date = datetime.datetime.strptime(scan_qt, '%Y%m')
#                 quarter_code = calcQuarterCode(scan_date)
#
#                 shares = None
#                 try:
#                     shares = DartManager.instance().get_dart().report(event_info.event_code, '주식총수', scan_date.year,
#                                                                       quarter_code)
#                 except Exception as e:
#                     logger.exception('get request error')
#                     if isinstance(e, ValueError):
#                         if isinstance(e.args, tuple) and e.args[0].startswith('could not find'):
#                             logger.error('could not find corps code {}. skip.'.format(event_info.event_name))
#                         elif isinstance(e.args, dict) and (e.args['status'] == '020' or e.args['status'] == '800'
#                                                            or e.args['status'] == '901'):
#                             STOP_SHARES_TF = True
#                             StockBatchManager.instance().set_retry_shares(False)
#                             break
#                     else:
#                         STOP_SHARES_TF = True
#                         StockBatchManager.instance().set_retry_shares(True)
#                         break
#                 # logger.info('finstate = {}'.format(finstate))
#                 if shares is not None:
#                     try:
#                         stock_tot_co = 0  # 총 발행 주식수
#                         stock_normal_co = 0  # 보통주 발행 주식수
#                         stock_prior_co = 0  # 우선주 발행 주식수
#                         distb_stock_tot_co = 0  # 총 유통 주식수
#                         distb_stock_normal_co = 0  # 보통주 유통 주식수
#                         distb_stock_prior_co = 0  # 우선주 유통 주식수
#                         tes_stock_tot_co = 0  # 총 자기 주식수
#                         tes_stock_normal_co = 0  # 보통주 자기 주식수
#                         tes_stock_prior_co = 0  # 우선주 자기 주식수
#
#                         stock_tot_co_org = shares.loc[DartStockSharesConfig().tot_condition(shares)].iloc[0][
#                             DartStockSharesConfig().column_pub_stock]
#                         stock_tot_co = 0 if stock_tot_co_org == '' or stock_tot_co_org == '-' else int(
#                             stock_tot_co_org.replace(',', ''))
#
#                         stock_normal_co_org = shares.loc[DartStockSharesConfig().normal_condition(shares)].iloc[0][
#                             DartStockSharesConfig().column_pub_stock]
#                         stock_normal_co = 0 if stock_normal_co_org == '' or stock_normal_co_org == '-' else int(
#                             stock_normal_co_org.replace(',', ''))
#
#                         stock_prior_co_org = shares.loc[DartStockSharesConfig().prior_condition(shares)].iloc[0][
#                             DartStockSharesConfig().column_pub_stock]
#                         stock_prior_co = 0 if stock_prior_co_org == '' or stock_prior_co_org == '-' else int(
#                             stock_prior_co_org.replace(',', ''))
#
#                         distb_stock_tot_co_org = shares.loc[DartStockSharesConfig().tot_condition(shares)].iloc[0][
#                             DartStockSharesConfig().column_dist_stock]
#                         distb_stock_tot_co = 0 if distb_stock_tot_co_org == '' or distb_stock_tot_co_org == '-' else int(
#                             distb_stock_tot_co_org.replace(',', ''))
#
#                         distb_stock_normal_co_org = \
#                             shares.loc[DartStockSharesConfig().normal_condition(shares)].iloc[0][
#                                 DartStockSharesConfig().column_dist_stock]
#                         distb_stock_normal_co = 0 if distb_stock_normal_co_org == '' or distb_stock_normal_co_org == '-' else int(
#                             distb_stock_normal_co_org.replace(',', ''))
#
#                         distb_stock_prior_co_org = shares.loc[DartStockSharesConfig().prior_condition(shares)].iloc[0][
#                             DartStockSharesConfig().column_dist_stock]
#                         distb_stock_prior_co = 0 if distb_stock_prior_co_org == '' or distb_stock_prior_co_org == '-' else int(
#                             distb_stock_prior_co_org.replace(',', ''))
#
#                         tes_stock_tot_co_org = shares.loc[DartStockSharesConfig().tot_condition(shares)].iloc[0][
#                             DartStockSharesConfig().column_own_stock]
#                         tes_stock_tot_co = 0 if tes_stock_tot_co_org == '' or tes_stock_tot_co_org == '-' else int(
#                             tes_stock_tot_co_org.replace(',', ''))
#
#                         tes_stock_normal_co_org = shares.loc[DartStockSharesConfig().normal_condition(shares)].iloc[0][
#                             DartStockSharesConfig().column_own_stock]
#                         tes_stock_normal_co = 0 if tes_stock_normal_co_org == '' or tes_stock_normal_co_org == '-' else int(
#                             tes_stock_normal_co_org.replace(',', ''))
#
#                         tes_stock_prior_co_org = shares.loc[DartStockSharesConfig().prior_condition(shares)].iloc[0][
#                             DartStockSharesConfig().column_own_stock]
#                         tes_stock_prior_co = 0 if tes_stock_prior_co_org == '' or tes_stock_prior_co_org == '-' else int(
#                             tes_stock_prior_co_org.replace(',', ''))
#
#                         entry = StockShares(
#                             **{'stock_event_id': event_info.stock_event_id, 'quarter': scan_qt,
#                                'stock_tot_co': stock_tot_co, 'stock_normal_co': stock_normal_co,
#                                'stock_prior_co': stock_prior_co, 'distb_stock_tot_co': distb_stock_tot_co,
#                                'distb_stock_normal_co': distb_stock_normal_co,
#                                'distb_stock_prior_co': distb_stock_prior_co, 'tes_stock_tot_co': tes_stock_tot_co,
#                                'tes_stock_normal_co': tes_stock_normal_co, 'tes_stock_prior_co': tes_stock_prior_co,
#                                })
#                         entry.save()
#                     except Exception as e:
#                         logger.exception(
#                             '{}error occured. event_name = {} / event_code = {} / scan_qt={}'.format(
#                                 logger_method, event_info.event_name, event_info.event_code, scan_qt))
#
#                 # 다음 분기 계산
#                 scan_qt = calcNextQuarter(scan_qt)
#                 time.sleep(FUND_API_REQUEST_TERM)
#     except Exception as e:
#         STOP_SHARES_TF = True
#         StockBatchManager.instance().set_retry_shares(False)
#         logger.exception('{} error occured. stop request')
#     return STOP_SHARES_TF


def calcQuarter(quarter_date):
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
    return str(quarter_date.year) + quarter_month


# 8년전 1분기를 계산할수 있는 가장 오래된 분기로 설정.
def calcFirstQuarterOfMinYear(quarter_date):
    qt = datetime.date(quarter_date.year - 8, 3, 1)
    return qt.strftime('%Y%m')


def calcQuarterCode(quarter_date: datetime.datetime):
    quarter = str(math.ceil(quarter_date.month / 3.0))
    if quarter == '1':
        return '11013'
    elif quarter == '2':
        return '11012'
    elif quarter == '3':
        return '11014'
    elif quarter == '4':
        return '11011'


def calcNextQuarter(qt: str):
    qt_origin = datetime.datetime.strptime(qt, '%Y%m')
    next_qt = qt_origin + relativedelta(months=3)
    return next_qt.strftime('%Y%m')


def calcBeforeQuarter(qt: str):
    qt_origin = datetime.datetime.strptime(qt, '%Y%m')
    before_qt = qt_origin - relativedelta(months=3)
    return before_qt.strftime('%Y%m')


def calcFirstQuarterOfNextYear(qt: str):
    qt_origin = datetime.datetime.strptime(qt, '%Y%m')
    # 해당년도 1분기가 DB에 등록되어있는지 조회
    qt_1 = datetime.date(qt_origin.year + 1, 3, 1)
    return qt_1.strftime('%Y%m')


def isIncludeRecent3Qt(cur_qt: str, scan_qt: str):
    # 스캔하는 분기가 현재분기포함 최근 3분기에 포함되는 분기명인지 조회
    cur_qt_time = datetime.datetime.strptime(cur_qt, '%Y%m')
    if scan_qt == cur_qt:
        return True
    elif scan_qt == (cur_qt_time - relativedelta(months=3)).strftime('%Y%m'):
        return True
    elif scan_qt == (cur_qt_time - relativedelta(months=6)).strftime('%Y%m'):
        return True
    else:
        return False

# def validateQuarter(qt: str, stock_event_id: int):
#     qt_origin = datetime.datetime.strptime(qt, '%Y%m')
#     # 해당년도 1분기가 DB에 등록되어있는지 조회
#     qt_1 = datetime.date(qt_origin.year, 3, 1)
#     qt_1_str = qt_1.strftime('%Y%m')
#     recent_quarter = FinancialStatement.objects.filter(
#         stock_event_id=stock_event_id).filter(quarter__startswith=qt_1_str)
#     if recent_quarter.count() == 0:
#         return False
#     else:
#         return True
