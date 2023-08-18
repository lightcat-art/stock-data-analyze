from ..models import PriceInfo, InfoUpdateStatus, SimulResult, EventInfo, SimulParam
from pykrx.website import krx
from pykrx import stock
from datetime import timedelta, datetime
from django.db import transaction
import time

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
ps. 
* 장 시작 전에는 시가,고가,종가,저가 가 모두 0으로 조회됨.
'''
first = False  # 첫 insert 진행중 여부
insert_all = False  # 첫 insert 강제 실행 조작 여부


# def stock_batch():
#     print('stock_batch start')
#     manage_event_all()


def manage_event_init():
    print('manage_event_init start')
    global first
    global insert_all
    today_org = datetime.now()
    print('cur time = ', today_org)
    today = today_org.strftime('%Y%m%d')

    cur_event_info = EventInfo.objects.all()
    start_date_str = datetime.now().strftime('%Y%m%d')
    market_event_info = krx.get_market_ticker_and_name(date=start_date_str, market='ALL')

    whole_code_df = [{'event_code': k, 'event_name': v} for k, v in market_event_info.iteritems()]
    # 전체 기간 전체 종목 insert
    if cur_event_info.count() == 0 or insert_all:
        print('first batch start')
        first = True
        insert_all = False
        # test code
        # whole_code_df = [{'event_code': '005930'}]

        get_market_data_time_taken = 0.0
        insert_market_data_time_taken = 0.0
        insert_count = 0
        for item in whole_code_df:
            event_code = item['event_code']
            # 기존 등록된 종목인지 확인.
            event_info = EventInfo.objects.filter(event_code=event_code)
            if event_info.count() != 0:
                event_status = InfoUpdateStatus.objects.filter(stock_event_id=event_info.first().stock_event_id)
                if event_status.count() != 0:  # 이미 등록된 것이면 스킵.
                    print(item['event_code'], ' already inserted. skip inserting.')
                    continue
                else:  # 종목정보 INSERT 중, 비정상종료된 케이스로 간주하고 해당 종목정보들 삭제 후 재등록
                    print(item['event_code'], ' already inserted. but not completed. delete and re-insert.')
                    event_price = PriceInfo.objects.filter(stock_event_id=event_info.first().stock_event_id)
                    event_info.delete()
                    event_price.delete()

            # 신규종목일 경우에는 위의 로직을 무시하고, 기존정보가 없으므로 그냥 INSERT 된다.
            insert_count += 1
            print(item['event_code'], ' inserting.. inserting count = ', insert_count)
            # stockevent 테이블에 insert
            with transaction.atomic():
                entry = EventInfo(**item)
                entry.save()

            # print('event_code = ', event_code)
            event_info = EventInfo.objects.filter(event_code=event_code)
            start_get_market_data = datetime.now().timestamp()

            price_info_df = stock.get_market_ohlcv_by_date(fromdate='19000101', todate=today, ticker=event_code)
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
                for priceitem in price_info_df.to_dict('records'):
                    if priceitem['open'] != 0 and priceitem['high'] != 0 \
                            and priceitem['low'] != 0 and priceitem['close'] != 0:
                        entry = PriceInfo(**priceitem)
                        entry.stock_event_id = event_info.first().stock_event_id
                        entry.save()

            end_insert_market_data = datetime.now().timestamp()
            insert_market_data_time_taken += (end_insert_market_data - end_get_market_data)

            status_dict = {'table_type': 'P', 'mod_dt': datetime.now(), 'reg_dt': datetime.now(),
                           'stock_event_id': event_info.first().stock_event_id}
            event_status_insert = InfoUpdateStatus(**status_dict)
            event_status_insert.save()

        print('get market data time = ', get_market_data_time_taken)
        print('insert market data time = ', insert_market_data_time_taken)
        print('manage_event_init end')
        first = False
    else:
        print('skip init_manage_event.')


def manage_event_daily():
    print('manage_event_daily start')
    global first
    global insert_all
    today_org = datetime.now()
    print('cur time = ', today_org)
    today = today_org.strftime('%Y%m%d')

    cur_event_info = EventInfo.objects.all()
    start_date_str = datetime.now().strftime('%Y%m%d')
    market_event_info = krx.get_market_ticker_and_name(date=start_date_str, market='ALL')

    whole_code_df = [{'event_code': k, 'event_name': v} for k, v in market_event_info.iteritems()]
    # 하루단위 전체종목 insert
    if cur_event_info.count() != 0 and not insert_all:
        print('daily batch start')
        print('first_batch executing status = ', first)
        if not first:
            price_info_df = stock.get_market_ohlcv_by_ticker(date=today, market='ALL')
            # 시가,종가,고가,저가 가 모두 0이면 휴일으로 간주하고 스킵.
            holiday = (price_info_df[['시가', '고가', '저가', '종가']] == 0).all(axis=None)
            # stockprice 테이블 업데이트 - 신규/기존 종목
            # price_info_df = price_info.reset_index() # 종목코드를 컬럼으로 빼기.
            price_info_df.rename(
                columns={'티커': 'event_code', '시가': 'open', '종가': 'close', '거래량': 'volume', '고가': 'high',
                         '저가': 'low',
                         '거래대금': 'value', '등락률': 'up_down_rate'}, inplace=True)
            price_info_df['date'] = datetime.now()
            if not holiday:
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
                with transaction.atomic():
                    for delete_event_code in del_event_result:
                        del_event_info = EventInfo.objects.filter(event_code=delete_event_code)
                        if len(del_event_info) != 0:
                            # stockevent 테이블 업데이트 - 삭제 종목
                            del_event_info.delete()

                            del_event_id = del_event_info.first().stock_event_id
                            # stockprice 테이블 업데이트 - 삭제 종목
                            del_event_price = PriceInfo.objects.filter(stock_event_id=del_event_id)
                            del_event_price.delete()

                            # 관리상태정보 삭제
                            del_event_status = InfoUpdateStatus.objects.filter(stock_event_id=del_event_id)
                            del_event_status.delete()

                # stockevent 테이블 업데이트 - 신규 종목
                # db에 넣을 데이터 구성
                new_event_insert_db = [{'event_code': new_event_code, 'event_name': new_event_name}
                                       for new_event_code, new_event_name in new_event_result.items()]
                with transaction.atomic():
                    for item in new_event_insert_db:
                        entry = EventInfo(**item)
                        entry.save()

                # priceinfo 테이블 업데이트 - 기존종목과 신규종목
                with transaction.atomic():
                    for k, v in price_info_df.to_dict('index').items():
                        event_info = EventInfo.objects.filter(event_code=k)
                        event_status = InfoUpdateStatus.objects.filter(
                            stock_event_id=event_info.first().stock_event_id)

                        if (today_org - timedelta(
                                days=1)).date() > event_status.first().mod_dt:  # 실행날짜를 제외하고 1일이상 누락된 경우
                            print('실행날짜를 제외하고 1일이상 누락된 경우')
                            # 실행날짜를 제외한 업데이트 빠진 기간 insert
                            fromdate = (event_status.first().mod_dt + timedelta(days=1)).strftime('%Y%m%d')
                            todate = (today_org - timedelta(days=1)).strftime('%Y%m%d')
                            omit_price_info_df = stock.get_market_ohlcv_by_date(fromdate=fromdate, todate=todate,
                                                                                ticker=k)
                            if len(omit_price_info_df) != 0:  # 휴일에 의한 업데이트 시간차 발생 경우 제외
                                omit_price_info_df = omit_price_info_df.reset_index()
                                omit_price_info_df.rename(
                                    columns={'날짜': 'date', '시가': 'open', '종가': 'close', '거래량': 'volume', '고가': 'high',
                                             '저가': 'low',
                                             '거래대금': 'value', '등락률': 'up_down_rate'},
                                    inplace=True)
                                with transaction.atomic():
                                    for priceitem in omit_price_info_df.to_dict('records'):
                                        # 종목이 비활성화된것으로 간주
                                        if priceitem['open'] != 0 and priceitem['high'] != 0 \
                                                and priceitem['low'] != 0 and priceitem['close'] != 0:
                                            entry = PriceInfo(**priceitem)
                                            entry.stock_event_id = event_info.first().stock_event_id
                                            entry.save()

                        if event_status.first().mod_dt.strftime('%Y%m%d') == today:
                            print('금일 주가 UPDATE : ','code=',k,)
                            # 장 끝난 시점에 하루에 한번만 업데이트하는거면 스킵하고, 하루에 여러번 업데이트하는거면 해당날짜의 주가 계속 받아와서 업데이트해야함.
                            # -> 하루에 한번 실행이라도 처음 insert에 장중가가 반영될 경우를 대비해 업데이트하도록 함.
                            today_event_info = PriceInfo.objects.filter(stock_event_id=event_info.first().stock_event_id, date=today_org)
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
                            print('금일 주가 INSERT : ','code=',k,)
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
                            event_status.first().mod_dt = datetime.now()
                            event_status.first().save()
            else:
                print('it''s holiday. only update omitted event information about the last period')
                with transaction.atomic():
                    for k, v in price_info_df.to_dict('index').items():
                        event_info = EventInfo.objects.filter(event_code=k)
                        event_status = InfoUpdateStatus.objects.filter(
                            stock_event_id=event_info.first().stock_event_id)

                        if (today_org - timedelta(
                                days=1)).date() > event_status.first().mod_dt:  # 실행날짜를 제외하고 1일이상 누락된 경우
                            # 업데이트 빠진 기간 insert
                            fromdate = (event_status.first().mod_dt + timedelta(days=1)).strftime('%Y%m%d')
                            todate = (today_org - timedelta(days=1)).strftime('%Y%m%d')
                            omit_price_info_df = stock.get_market_ohlcv_by_date(fromdate=fromdate, todate=todate,
                                                                                ticker=k)
                            if len(omit_price_info_df) != 0:  # 휴일에 의한 업데이트 시간차 발생 경우 제외
                                omit_price_info_df = omit_price_info_df.reset_index()
                                omit_price_info_df.rename(
                                    columns={'날짜': 'date', '시가': 'open', '종가': 'close', '거래량': 'volume', '고가': 'high',
                                             '저가': 'low',
                                             '거래대금': 'value', '등락률': 'up_down_rate'},
                                    inplace=True)
                                with transaction.atomic():
                                    for priceitem in omit_price_info_df.to_dict('records'):
                                        # 종목이 비활성화된것으로 간주
                                        if priceitem['open'] != 0 and priceitem['high'] != 0 \
                                                and priceitem['low'] != 0 and priceitem['close'] != 0:
                                            entry = PriceInfo(**priceitem)
                                            entry.stock_event_id = event_info.first().stock_event_id
                                            entry.save()
                            print('event code ', k, ' : updating omitted informations complete')

                        event_status = InfoUpdateStatus.objects.filter(
                            stock_event_id=event_info.first().stock_event_id)
                        if len(event_status) == 0:
                            status_dict = {'table_type': 'P', 'mod_dt': datetime.now(), 'reg_dt': datetime.now(),
                                           'stock_event_id': event_info.first().stock_event_id}
                            event_status_insert = InfoUpdateStatus(**status_dict)
                            event_status_insert.save()
                        else:
                            for item in event_status:
                                item.mod_dt = datetime.now()
                                item.save()
                        time.sleep(0.3)

        else:
            print('first batch executing, so skip daily batch')
    print('manage_event_daily end')

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
