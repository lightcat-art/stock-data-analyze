import datetime
from datetime import timedelta
from time import strptime, mktime
import json
from django.db import transaction

from django.shortcuts import render, get_object_or_404, redirect

from .analyze.core import Core
from .forms import StockSimulParamForm
from .models import StockSimulParam
from .models import StockPrice, StockInfoUpdateStatus, StockEvent
from pykrx.website.krx.market import wrap
from pykrx import stock


def stock_simul_param(request):
    if request.method == "POST":
        form = StockSimulParamForm(request.POST)
        if form.is_valid():  # 모든 필드에 값이 있어야 하고, 잘못된 값이 있다면 저장되지 않도록 체크.
            simul_param = form.save(commit=False)  # 폼을 저장하지만, 바로 모델에 저장하지 않도록 commit옵션 False
            simul_param.save()
            return redirect('stock_simul_result', pk=simul_param.pk)
    else:
        form = StockSimulParamForm()
    return render(request, 'stocksimul/stock_simul_param.html', {'form': form})


def stock_simul_result(request, pk):
    simul_param = get_object_or_404(StockSimulParam, pk=pk)
    print(simul_param.start_date)
    print(simul_param.days)
    print(simul_param.event_name)

    event_name = simul_param.event_name
    end_date = (simul_param.start_date + timedelta(days=simul_param.days)).strftime('%Y%m%d')
    start_date = simul_param.start_date.strftime('%Y%m%d')
    print(start_date)
    print(end_date)

    # 종목정보 업데이트 날짜주기
    EVENT_INFO_UPDATE_PERIOD = 3

    event_info_status = StockInfoUpdateStatus.objects.filter(table_type='E')
    print('event_info_status={}'.format(event_info_status))
    print('event_info_status count={}'.format(event_info_status.count()))
    print('current time={}'.format(datetime.datetime.now()))
    if event_info_status.count() != 0:
        print('last mod date = {}'.format(event_info_status.mod_dt))
        print(datetime.datetime.now() - event_info_status.mod_dt)

    if event_info_status.count() == 0 or (datetime.datetime.now() - event_info_status.mod_dt) \
            > timedelta(days=EVENT_INFO_UPDATE_PERIOD):
        whole_code_df = wrap.get_market_ticker_and_name(date=start_date, market='ALL')
        whole_code_df = [{'event_code': k, 'event_name': v} for k, v in whole_code_df.iteritems()]
        print('1')
        with transaction.atomic():
            for item in whole_code_df:
                entry = StockEvent(**item)
                entry.save()
        print('2')

        if event_info_status.count() == 0:
            status_dict = {'table_type': 'E', 'mod_dt': datetime.datetime.now(), 'reg_dt': datetime.datetime.now()}
            event_info_status = StockInfoUpdateStatus(**status_dict)
        else:
            event_info_status.mod_dt = datetime.datetime.now()
        event_info_status.save()
        print('3')
    else:
        print("event_info_status doesn't have to update. last update date is {}".format(event_info_status.mod_dt))

    event_info = get_object_or_404(StockEvent, event_name=event_name)
    print('event_name={}, event_info={}'.format(event_name, event_info))
    print('stock_event_id = {}'.format(event_info.stock_event_id))
    # 종목별 주가정보 업데이트 날짜주기
    PRICE_INFO_UPDATE_PERIOD = 1
    today = datetime.datetime.now().strftime('%Y%m%d')
    price_info_status = StockInfoUpdateStatus.objects.filter(table_type='P') \
        .filter(detail_info_1=event_info.stock_event_id)
    if price_info_status.count() == 0 or (datetime.datetime.now() - price_info_status.mod_dt) \
            > timedelta(days=PRICE_INFO_UPDATE_PERIOD):
        info_none_yn = price_info_status.count() == 0
        if info_none_yn:
            update_start_dt = '2000-01-01'
        else:
            update_start_dt = (price_info_status.mod_dt + timedelta(days=1)).strftime('%Y%m%d')
        price_info_df = stock.get_market_ohlcv_by_date(update_start_dt, today, event_info.event_code)
        price_info_df = price_info_df.reset_index()
        price_info_df.rename(
            columns={'날짜': 'date', '시가': 'open', '종가': 'close', '거래량': 'volume', '고가': 'high', '저가': 'low'},
            inplace=True)
        with transaction.atomic():
            for item in price_info_df.to_dict('records'):
                # if StockPrice.objects.filter(date=item['date']).filter(event_code=event_info.event_code).count() < 1:
                entry = StockPrice(**item)
                entry.event_code = event_info.event_code
                entry.stock_event_id = event_info.stock_event_id
                entry.save()

    simul_start_date = datetime.datetime.strptime(start_date, '%Y%m%d')
    simul_end_date = datetime.datetime.strptime(end_date, '%Y%m%d')
    stocks = StockPrice.objects.filter(event_code=event_info.event_code) \
        .filter(date__gte=simul_start_date, date_lte=simul_end_date).order_by('date')

    chart_data = make_chart_data(stocks, event_name)

    return render(request, 'stocksimul/stock_simul_result.html', {'chart_data': chart_data})


# def stock_simul_graph(request, event_code, event_name):
#     stocks = StockPrice.objects.filter(event_code=event_code).order_by('date')
#     chart_data = make_chart_data(stocks, event_name)
#     return chart_data


def make_chart_data(stocks, event_name):
    '''
    :param stocks: StockPrice 객체 리스트
    :param event_name: 종목명
    :return:
    '''
    chart_data = {}
    close_list = []
    open_list = []
    for stock in stocks:
        time_tuple = strptime(str(stock.date), '%Y-%m-%d')
        utc_now = mktime(time_tuple) * 1000
        close_list.append([utc_now, stock.close])
        open_list.append([utc_now, stock.open])

    # chart_data = {
    #     'chart': {'height': 500},
    #     'title': {'text': event_name},
    #     'setOptions': {'global': {'useUTC': 'false'}},
    #     'xAxis': {
    #         'type': 'date',
    #         'lables': {
    #         }
    #     }
    # }

    chart_data = {
        'close': close_list,
        'open': open_list,
        'name': event_name
    }
    # chart_data = json.dumps(chart_data)

    return chart_data
