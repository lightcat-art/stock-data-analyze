from ..models import StockPrice, StockInfoUpdateStatus, StockSimulResult, StockEvent, StockSimulParam
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
    2. 몇몇 종목은 삭제된 종목일수 있음.
        2. 삭제된 종목의 경우에는 주가정보와 종목정보를 삭제조치.
'''


def stock_batch():
    print('stock_batch start')
    manage_event()
    # manage_event_price(event_result)


def manage_event():
    cur_event_info = StockEvent.objects.all()
    start_date_str = datetime.now().strftime('%Y%m%d')
    market_event_info = krx.get_market_ticker_and_name(date=start_date_str, market='ALL')

    today = datetime.now().strftime('%Y%m%d')
    print('today = ', today)
    whole_code_df = [{'event_code': k, 'event_name': v} for k, v in market_event_info.iteritems()]

    # 전체 기간 전체 종목 insert
    if cur_event_info.count() == 0:
        # stockevent 테이블에 insert
        with transaction.atomic():
            for item in whole_code_df:
                entry = StockEvent(**item)
                entry.save()

        # stockprice 테이블에 insert

        # test code
        whole_code_df = [{'event_code': '005930'}]

        get_market_data_time_taken = 0.0
        insert_market_data_time_taken = 0.0
        for item in whole_code_df:
            event_code = item['event_code']
            print('event_code = ', event_code)
            event_info_qryset = StockEvent.objects.filter(event_code=event_code)
            start_get_market_data = datetime.now().timestamp()

            price_info_df = stock.get_market_ohlcv_by_date(fromdate='19000101', todate=today, ticker=event_code)
            print('price_info = ', price_info_df)
            end_get_market_data = datetime.now().timestamp()
            get_market_data_time_taken += (end_get_market_data - start_get_market_data)

            price_info_df = price_info_df.reset_index()
            price_info_df.rename(
                columns={'날짜': 'date', '시가': 'open', '종가': 'close', '거래량': 'volume', '고가': 'high', '저가': 'low',
                         '거래대금': 'value', '등락률': 'up_down_rate'},
                inplace=True)
            with transaction.atomic():
                for priceitem in price_info_df.to_dict('records'):
                    # if StockPrice.objects.filter(date=item['date']).filter(event_code=event_info.event_code).count() < 1:
                    entry = StockPrice(**priceitem)
                    entry.stock_event_id = event_info_qryset.first().stock_event_id
                    entry.save()

            end_insert_market_data = datetime.now().timestamp()
            insert_market_data_time_taken += (end_insert_market_data - end_get_market_data)

            '''stockinfoupdatestatus 테이블에 데이터상태 업데이트 - 삭제 종목에 대해 상태업데이트를 관리하기 어려우므로, 기능 일시제거
            이미 신규, 기존, 삭제 종목에 대해 구분이 완료된 상황이므로 업데이트 안해도 상관없음.'''
            # status_dict = {'table_type': 'P', 'mod_dt': datetime.now(), 'reg_dt': datetime.now(),
            #                'stock_event_id': event_info_qryset.first().stock_event_id}
            # event_info_status_model = StockInfoUpdateStatus(**status_dict)
            # event_info_status_model.save()

        print('get market data time = ', get_market_data_time_taken)
        print('insert market data time = ', insert_market_data_time_taken)
        print('end insert stock data')

    # 하루단위 전체종목 insert
    else:
        new_event_result = {}
        del_event_result = []
        # delete 항목을 따로 나중에 제외시키기 위해 미리 모두 다 넣어둠.
        for market_event_code, market_event_name in market_event_info:
            del_event_result.append(market_event_code)
        # 등록되어있는 종목, 신규종목, 삭제될 종목 구분.
        for market_event_code, market_event_name in market_event_info:
            code_exist = False
            code_new = False
            code_delete = False
            for cur_event_info in cur_event_info:
                if cur_event_info.event_code == market_event_code:
                    code_exist = True
                    # event_result['exist'].append(item['event_code'])
                    # 현재 시장에서 존재하는 종목이 db에서 존재한다면 그 외에는 모두 삭제될 종목이라는 점을 이용하여 필터링.
                    del_event_result.remove(market_event_code)

            if not code_exist:
                code_new = True
                new_event_result.update({market_event_code:market_event_name})

        # stockevent 테이블 업데이트 - 삭제 종목
        del_event_id_list = []
        with transaction.atomic():
            for delete_event_code in del_event_result:
                del_event_info = StockEvent.objects.filter(event_code=delete_event_code)
                del_event_id_list.append(del_event_info.stock_event_id)
                del_event_info.delete()

        # stockprice 테이블 업데이트 - 삭제 종목
        with transaction.atomic():
            for del_event_id in del_event_id_list:
                del_event_price = StockPrice.objects.filter(stock_event_id=del_event_id)
                del_event_price.delete()

        # stockevent 테이블 업데이트 - 신규 종목
        # db에 넣을 데이터 구성
        new_event_insert_db = [{'event_code':new_event_code, 'event_name': new_event_name}
                               for new_event_code, new_event_name in new_event_result.items()]
        with transaction.atomic():
            for item in new_event_insert_db:
                entry = StockEvent(**item)
                entry.save()

        # stockprice 테이블 업데이트 - 신규/기존 종목
        price_info_df = stock.get_market_ohlcv_by_ticker(date=today)
        # price_info_df = price_info.reset_index() # 종목코드를 컬럼으로 빼기.
        price_info_df.rename(
            columns={'티커': 'event_code', '시가': 'open', '종가': 'close', '거래량': 'volume', '고가': 'high', '저가': 'low',
                     '거래대금': 'value', '등락률': 'up_down_rate'}, inplace=True)
        with transaction.atomic():
            for k, v in price_info_df.to_dict('index').items():
                event_info_qryset = StockEvent.objects.filter(event_code=k)
                entry = StockPrice(**v)
                entry.stock_event_id = event_info_qryset.first().stock_event_id
                entry.save()

    '''stockinfoupdatestatus 테이블에 데이터상태 업데이트 - 삭제 종목에 대해 상태업데이트를 관리하기 어려우므로, 기능 일시제거
    이미 신규, 기존, 삭제 종목에 대해 구분이 완료된 상황이므로 업데이트 안해도 상관없음.'''
    # status_dict = {'table_type': 'E', 'mod_dt': datetime.now(), 'reg_dt': datetime.now()}
    # event_info_status_model = StockInfoUpdateStatus(**status_dict)
    # event_info_status_model.save()

