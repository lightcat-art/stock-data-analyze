import datetime
import json
from datetime import timedelta
from time import strptime, mktime

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from pykrx import stock
from pykrx.website.krx.market import wrap

from .forms import StockSimulParamForm
from .models import StockPrice, StockInfoUpdateStatus, StockEvent, StockSimulParam


def stock_simul_param(request):
    event_list = StockEvent.objects.all
    # event_list = (('삼성전자','삼성전자'),('삼성생명','삼성생명'))
    # print('event_list = ',event_list)
    if request.method == "POST":
        print(request.POST)
        form = StockSimulParamForm(request.POST)
        # print('stock_simul_param input = ', form)
        if form.is_valid():  # 모든 필드에 값이 있어야 하고, 잘못된 값이 있다면 저장되지 않도록 체크.
            simul_param = form.save(commit=False)  # 폼을 저장하지만, 바로 모델에 저장하지 않도록 commit옵션 False
            # print('stock_simul_param input = ', simul_param.event_name)
            simul_param.save()
            return redirect('stock_simul_result', pk=simul_param.pk)
    else:
        form = StockSimulParamForm()
    return render(request, 'stocksimul/stock_simul_param.html', {'form': form, 'show_event':event_list})


def stock_simul_result(request, pk):
    simul_param = get_object_or_404(StockSimulParam, pk=pk)
    print('input param : start_date = {}'.format(simul_param.start_date))
    print('input param : days = {}'.format(simul_param.days))
    print('input param : event_name = {}'.format(simul_param.event_name))

    event_name = simul_param.event_name
    start_date = simul_param.start_date.strftime('%Y%m%d')
    end_date = (simul_param.start_date + timedelta(days=simul_param.days)).strftime('%Y%m%d')
    # print(start_date)
    # print(end_date)

    update_event_info(start_date)

    event_info = get_object_or_404(StockEvent, event_name=event_name)
    # print('event_name={}, event_info={}'.format(event_name, event_info))
    # print('stock_event_id = {}'.format(event_info.stock_event_id))

    update_stock_price(event_info)

    simul_start_date = datetime.datetime.strptime(start_date, '%Y%m%d')
    simul_end_date = datetime.datetime.strptime(end_date, '%Y%m%d')
    stocks = StockPrice.objects.filter(stock_event_id=event_info.stock_event_id) \
        .filter(date__gte=simul_start_date, date__lte=simul_end_date).order_by('date')

    chart_data, gui_ohlc, gui_volume, gui_whole = make_chart_data(stocks, event_name)

    return render(request, 'stocksimul/stock_simul_result.html', {'chart_data': chart_data, 'gui_ohlc':gui_ohlc,
                                                                  'gui_volume':gui_volume, 'gui_whole':gui_whole,
                                                                  'event_name':event_name})


def update_stock_price(event_info):
    '''
    종목별 주가정보 업데이트
    :param event_info: 특정 종목에 해당하는 StockEvent 모델 객체
    :return:
    '''
    # 종목별 주가정보 업데이트 날짜주기
    PRICE_INFO_UPDATE_PERIOD = 1
    today = datetime.datetime.now().strftime('%Y%m%d')
    price_info_status_qryset = StockInfoUpdateStatus.objects.filter(table_type='P') \
        .filter(stock_event_id=event_info.stock_event_id)
    # price_info_status = StockInfoUpdateStatus.objects.get(
    #     Q(table_type='P') & Q(stock_event_id=event_info.stock_event_id))
    if price_info_status_qryset.count() != 0:
        print('update_stock_price : last mod date = {}'.format(price_info_status_qryset.first().mod_dt))
        print('update_stock_price : date substract result = ',
              datetime.date.today() - price_info_status_qryset.first().mod_dt)
    if price_info_status_qryset.count() == 0 or (datetime.date.today() - price_info_status_qryset[0].mod_dt) \
            >= timedelta(days=PRICE_INFO_UPDATE_PERIOD):
        info_none_yn = price_info_status_qryset.count() == 0
        if info_none_yn:
            update_start_dt = '2000-01-01'
            status_dict = {'table_type': 'P', 'mod_dt': datetime.date.today(), 'reg_dt': datetime.date.today(),
                           'stock_event_id': event_info.stock_event_id}
            price_info_status_model = StockInfoUpdateStatus(**status_dict)
            price_info_status_model.save()
        else:
            update_start_dt = (price_info_status_qryset[0].mod_dt + timedelta(days=1)).strftime('%Y%m%d')
            price_info_status_model = price_info_status_qryset.first()
            price_info_status_model.mod_dt = datetime.date.today()
            price_info_status_model.save()
        print('2 price_info_status = ', price_info_status_qryset)

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
    else:
        print("price_info_status doesn't have to update. last modify date is {}"
              .format(price_info_status_qryset.first().mod_dt))


def update_event_info(start_date):
    '''
    전체 주식종목정보 업데이트
    :param start_date: 시뮬레이션 시작날짜 입력값
    :return:
    '''
    # 종목정보 업데이트 날짜주기
    EVENT_INFO_UPDATE_PERIOD = 3
    event_info_status_qryset = StockInfoUpdateStatus.objects.filter(table_type='E')
    # print('event_info_status={}'.format(event_info_status))
    # print('event_info_status count={}'.format(event_info_status.count()))
    # print('current time={}'.format(datetime.datetime.now()))
    if event_info_status_qryset.count() != 0:
        print('update_event_info : last mod date = {}'.format(event_info_status_qryset.first().mod_dt))
        print('update_event_info : date substract result = ',
              datetime.date.today() - event_info_status_qryset.first().mod_dt)
    if event_info_status_qryset.count() == 0 or (datetime.date.today() - event_info_status_qryset.first().mod_dt) \
            >= timedelta(days=EVENT_INFO_UPDATE_PERIOD):
        whole_code_df = wrap.get_market_ticker_and_name(date=start_date, market='ALL')
        whole_code_df = [{'event_code': k, 'event_name': v} for k, v in whole_code_df.iteritems()]
        # 종목코드가 변경되는 경우, 상장폐지 되는 경우, 신규상장되는 경우를 고려하여 업데이트 쿼리 작성 필요.
        # with transaction.atomic():
        #     for item in whole_code_df:
        #         entry = StockEvent(**item)
        #         entry.save()
        info_none_yn = event_info_status_qryset.count() == 0
        if info_none_yn:
            status_dict = {'table_type': 'E', 'mod_dt': datetime.datetime.now(), 'reg_dt': datetime.datetime.now()}
            event_info_status_model = StockInfoUpdateStatus(**status_dict)
            event_info_status_model.save()
        else:
            event_info_status_model = event_info_status_qryset.first()
            event_info_status_model.mod_dt = datetime.date.today()
            event_info_status_model.save()
    else:
        print("event_info_status doesn't have to update. last modify date is {}"
              .format(event_info_status_qryset.first().mod_dt))


# def stock_simul_graph(request, event_code, event_name):
#     stocks = StockPrice.objects.filter(event_code=event_code).order_by('date')
#     chart_data = make_chart_data(stocks, event_name)
#     return chart_data

def ajax_chart_data(request):
    print('ajax_chart_data start')
    # print('ajax_chart_data : event_name = {}'.format(event_name))
    print('ajax_chart_data : request body :', request.body)

    data = {'whole': [[123124124, 2324, 2323, 2323, 2323, 2323]]}
    return JsonResponse(data)

def make_chart_data(stocks, event_name):
    '''
    :param stocks: StockPrice 객체 리스트
    :param event_name: 종목명
    :return:
    '''
    print('make chart data start')
    chart_data = {}
    close_list = []
    open_list = []

    gui_ohlc = []
    gui_volume = []
    gui_whole = []
    print('make chart data : stocks = {}'.format(stocks))
    for stock in stocks:
        print('make chart data : stock = {}'.format(stock))
        time_tuple = strptime(str(stock.date), '%Y-%m-%d')
        utc_now = mktime(time_tuple) * 1000
        print(utc_now)
        close_list.append([utc_now, stock.close])
        open_list.append([utc_now, stock.open])

        gui_ohlc.append([utc_now, stock.open, stock.close, 9999, 8888])  # the date, open, high, low, close
        gui_volume.append([utc_now, 7777])

        gui_whole.append([utc_now, stock.open, 9999, 8888, stock.close, 777777])

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

    return chart_data, gui_ohlc, gui_volume, gui_whole
