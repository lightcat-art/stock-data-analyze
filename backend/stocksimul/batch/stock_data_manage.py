from ..models import StockPrice, StockInfoUpdateStatus, StockSimulResult, StockEvent, StockSimulParam
from pykrx.website import krx
from pykrx import stock
from datetime import timedelta, datetime
from django.db import transaction
import time


def stock_batch():
    print('stock_batch start')
    insert_stock_data()


def insert_stock_event():
    event_info_qryset = StockInfoUpdateStatus.objects.filter(table_type='E')
    whole_code_df = None
    if event_info_qryset.count() == 0:
        # stockevent 테이블에 insert
        start_date_str = datetime.now().strftime('%Y%m%d')
        whole_code_df = krx.get_market_ticker_and_name(date=start_date_str, market='ALL')
        print('whole_code_df =',whole_code_df)
        whole_code_df = [{'event_code': k, 'event_name': v} for k, v in whole_code_df.iteritems()]
        with transaction.atomic():
            for item in whole_code_df:
                entry = StockEvent(**item)
                entry.save()

        # stockinfoupdatestatus 테이블에 데이터상태 업데이트
        status_dict = {'table_type': 'E', 'mod_dt': datetime.now(), 'reg_dt': datetime.now()}
        event_info_status_model = StockInfoUpdateStatus(**status_dict)
        event_info_status_model.save()
    return whole_code_df


def insert_stock_data():
    print('start insert stock data')
    today = datetime.now().strftime('%Y%m%d')
    print('today = ',today)
    price_info_status_qryset = StockInfoUpdateStatus.objects.filter(table_type='P')
    if price_info_status_qryset.count() == 0:  # 전체 기간 전체 종목 insert
        # 종목 정보가 아예 없는것으로 간주하고 stockevent 테이블 insert
        whole_code_df = insert_stock_event()

        # test code
        whole_code_df = [{'event_code':'005930'}]

        # stockprice 테이블 insert
        get_market_data = 0.0
        insert_market_data = 0.0
        for item in whole_code_df:
            event_code = item['event_code']
            print('event_code = ', event_code)
            event_info_qryset = StockEvent.objects.filter(event_code=event_code)
            start_get_market_data = datetime.now().timestamp()

            price_info_df = stock.get_market_ohlcv_by_date(fromdate='19000101', todate=today, ticker=event_code)
            print('price_info = ', price_info_df)
            end_get_market_data = datetime.now().timestamp()
            get_market_data += (end_get_market_data - start_get_market_data)

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
            insert_market_data += (end_insert_market_data - end_get_market_data)

            status_dict = {'table_type': 'P', 'mod_dt': datetime.now(), 'reg_dt': datetime.now(),
                           'stock_event_id': event_info_qryset.first().stock_event_id}
            event_info_status_model = StockInfoUpdateStatus(**status_dict)
            event_info_status_model.save()

        print('get market data time = ',get_market_data)
        print('insert market data time = ',insert_market_data)

        print('end insert stock data')


    else:  # 하루단위 전체 종목 insert
        pass
