import datetime
import time
from datetime import timedelta
from time import strptime, mktime

from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from plotly.subplots import make_subplots
from pykrx.website.krx.market import wrap
import plotly.graph_objects as go

from .config import stockConfig
from .forms import StockSimulParamForm
from .models import StockPrice, StockInfoUpdateStatus, StockEvent, StockSimulParam

stock_price_init_start_dt = '2000-01-01'


def stock_simul_param(request):
    event_list = StockEvent.objects.all
    # event_list = (('삼성전자','삼성전자'),('삼성생명','삼성생명'))
    # print('event_list = ',event_list)
    # if request.method == "POST":
    #     print(request.POST)
    #     form = StockSimulParamForm(request.POST)
    #     # print('stock_simul_param input = ', form)
    #     if form.is_valid():  # 모든 필드에 값이 있어야 하고, 잘못된 값이 있다면 저장되지 않도록 체크.
    #         simul_param = form.save(commit=False)  # 폼을 저장하지만, 바로 모델에 저장하지 않도록 commit옵션 False
    #         # print('stock_simul_param input = ', simul_param.event_name)
    #         simul_param.save()
    #         return redirect('stock_simul_result', pk=simul_param.pk)
    if request.is_ajax():  # request.method == "POST": 로 하여도 ajax가 POST로 들어오기 때문에 인식가능.
        form = StockSimulParamForm(request.POST or None)
        data = {}
        if form.is_valid():
            # event_name = form.cleaned_data.get('event_name')
            # start_date = form.cleaned_data.get('start_date')
            # days = form.cleaned_data.get('days')
            # print('stock_simul_param : ajax : event_name = {}, start_date = {}, days = {}'
            #       .format(event_name, start_date, days))
            simul_param = form.save(commit=False)
            simul_param.save()
            print('stock_simul_param : ajax model data : event_name = {}, start_date = {}, days = {}'
                  .format(simul_param.event_name, simul_param.start_date, simul_param.days))

            # simul_param = get_object_or_404(StockSimulParam, pk=simul_param.pk)

            event_name = simul_param.event_name
            start_date_str = simul_param.start_date.strftime('%Y%m%d')
            end_date_str = (simul_param.start_date + timedelta(days=simul_param.days)).strftime('%Y%m%d')

            update_event_info(start_date_str)
            try:
                event_info = StockEvent.objects.get(event_name=event_name)
            except StockEvent.DoesNotExist as e:
                # render_to_response method is deprecated.
                return render(request, 'stocksimul/error_msg.html', {'error_type': 'MNE',
                                                                     'event_name': event_name, 'exception': e})
            update_stock_price(event_info)

            data['event_name'] = form.cleaned_data.get('event_name')
            data['start_date_str'] = start_date_str
            data['end_date_str'] = end_date_str
            data['status'] = 'ok'
            return JsonResponse(data)
    else:
        form = StockSimulParamForm()
    return render(request, 'stocksimul/stock_simul_param.html', {'form': form, 'show_event': event_list})


def render_stock_simul_result(request, event_name, start_date_str, end_date_str):
    # print('render_stock_simul_result : request = ', request.POST)
    # event_name = request.POST.get('event_name')
    # start_date_str = request.POST.get('start_date_str')
    # end_date_str = request.POST.get('end_date_str')
    # print('render_stock_simul_result : ajax param event_name = {}, start_date = {}, end_date = {}'.format(event_name, start_date_str, end_date_str))
    print('render_stock_simul_result : url param event_name = {}, start_date = {}, end_date = {}'.format(event_name, start_date_str, end_date_str))
    return render(request, 'stocksimul/stock_simul_result.html', {'event_name': event_name,
                                                                  'start_date_str': start_date_str,
                                                                  'end_date_str': end_date_str})


def stock_simul_result(request, pk):
    simul_param = get_object_or_404(StockSimulParam, pk=pk)
    print('input param : start_date = {}'.format(simul_param.start_date))
    print('input param : days = {}'.format(simul_param.days))
    print('input param : event_name = {}'.format(simul_param.event_name))

    event_name = simul_param.event_name
    start_date_str = simul_param.start_date.strftime('%Y%m%d')
    end_date_str = (simul_param.start_date + timedelta(days=simul_param.days)).strftime('%Y%m%d')
    # print(start_date)
    # print(end_date)

    update_event_info(start_date_str)

    try:
        event_info = StockEvent.objects.get(event_name=event_name)
    except StockEvent.DoesNotExist as e:
        # render_to_response method is deprecated.
        return render(request, 'stocksimul/error_msg.html', {'error_type': 'MNE',
                                                             'event_name': event_name, 'exception': e})

    # event_info = get_object_or_404(StockEvent, event_name=event_name)
    # print('event_name={}, event_info={}'.format(event_name, event_info))
    # print('stock_event_id = {}'.format(event_info.stock_event_id))

    update_stock_price(event_info)

    # simul_start_date = datetime.datetime.strptime(start_date_str, '%Y%m%d')
    # simul_end_date = datetime.datetime.strptime(end_date_str, '%Y%m%d')
    # stocks = StockPrice.objects.filter(stock_event_id=event_info.stock_event_id) \
    #     .filter(date__gte=simul_start_date, date__lte=simul_end_date).order_by('date')
    #
    # graph = make_chart_data(stocks, event_name)
    # print(graph)
    return render(request, 'stocksimul/stock_simul_result.html', {'event_name': event_name,
                                                                  'start_date_str': start_date_str,
                                                                  'end_date_str': end_date_str})


# def ajax_chart_data(request):
#     print('ajax_chart_data start')
#     # print('ajax_chart_data : event_name = {}'.format(event_name))
#     # print('ajax_chart_data : request body :', request.body)
#     # print('ajax_chart_data : request POST info :', request.POST)
#     print('ajax_chart_data : request GET info :', request.GET)
#     # json_object = json.loads(request.GET)
#     event_name = request.GET.get('event_name')
#     start_date_str = request.GET.get('start_date_str')
#     end_date_str = request.GET.get('end_date_str')
#     event_info = get_object_or_404(StockEvent, event_name=event_name)
#     simul_start_date = datetime.datetime.strptime(start_date_str, '%Y%m%d')
#     simul_end_date = datetime.datetime.strptime(end_date_str, '%Y%m%d')
#     stocks = StockPrice.objects.filter(stock_event_id=event_info.stock_event_id) \
#         .filter(date__gte=simul_start_date, date__lte=simul_end_date).order_by('date')
#
#     # data = {'whole': [[123124124, 2324, 2323, 2323, 2323, 2323]]}
#     ajax_gui_whole = []
#     print('ajax_chart_data : stocks = {}'.format(stocks))
#     for stock in stocks:
#         time_tuple = strptime(str(stock.date), '%Y-%m-%d')
#         utc_now = mktime(time_tuple) * 1000
#         ajax_gui_whole.append([utc_now, stock.open, stock.high, stock.low, stock.close, stock.volume])
#
#     response = {}
#     response.update({'chart_data': ajax_gui_whole})
#     return JsonResponse(response)


def ajax_plotly_chart_data(request):
    print('ajax_plotly_chart_data')
    # print('ajax_chart_data : event_name = {}'.format(event_name))
    # print('ajax_chart_data : request body :', request.body)
    # print('ajax_chart_data : request POST info :', request.POST)
    print('ajax_plotly_chart_data : request GET info :', request.GET)
    # json_object = json.loads(request.GET)
    event_name = request.GET.get('event_name')
    start_date_str = request.GET.get('start_date_str')
    end_date_str = request.GET.get('end_date_str')
    event_info = get_object_or_404(StockEvent, event_name=event_name)
    simul_start_date = datetime.datetime.strptime(start_date_str, '%Y%m%d')
    simul_end_date = datetime.datetime.strptime(end_date_str, '%Y%m%d')
    stocks = StockPrice.objects.filter(stock_event_id=event_info.stock_event_id) \
        .filter(date__gte=simul_start_date, date__lte=simul_end_date).order_by('date')

    # data = {'whole': [[123124124, 2324, 2323, 2323, 2323, 2323]]}
    # print('ajax_plotly_chart_data : stocks = {}'.format(stocks))
    open = []
    close = []
    high = []
    low = []
    date = []
    volume = []
    for stock in stocks:
        time_tuple = stock.date.strftime('%Y/%m/%d')
        date.append(time_tuple)
        open.append(stock.open)
        close.append(stock.close)
        low.append(stock.low)
        high.append(stock.high)
        volume.append(stock.volume)

    response = {}
    response.update({'date': date, 'open': open, 'close': close, 'high': high, 'low': low, 'volume': volume})
    return JsonResponse(response)


def update_stock_price(event_info):
    '''
    종목별 주가정보 업데이트
    :param event_info: 특정 종목에 해당하는 StockEvent 모델 객체
    :return:
    '''

    today = datetime.datetime.now().strftime('%Y%m%d')
    price_info_status_qryset = StockInfoUpdateStatus.objects.filter(table_type='P') \
        .filter(stock_event_id=event_info.stock_event_id)
    # price_info_status = StockInfoUpdateStatus.objects.get(
    #     Q(table_type='P') & Q(stock_event_id=event_info.stock_event_id))
    info_none_yn = False
    info_update_yn = False
    info_del_ins_yn = False
    print('update_stock_price : info_status = ', price_info_status_qryset)
    if price_info_status_qryset.count() == 0:  # 이전에 해당 종목데이터가 업데이트된 이력이 없는 경우
        print('update_stock_price : first update for {}'.format(event_info.event_name))
        update_start_dt = stock_price_init_start_dt
        status_dict = {'table_type': 'P', 'mod_dt': datetime.date.today(), 'reg_dt': datetime.date.today(),
                       'stock_event_id': event_info.stock_event_id}
        price_info_status_model = StockInfoUpdateStatus(**status_dict)
        price_info_status_model.save()
        info_none_yn = True
    # 이전에 업데이트 된 이력이 있고, 업데이트 주기가 도달하거나 초과한 경우
    elif (datetime.date.today() - price_info_status_qryset[0].mod_dt) \
            >= timedelta(
        days=stockConfig.PRICE_INFO_UPDATE_PERIOD) and price_info_status_qryset.first().update_type == 'UD':
        print('update_stock_price : add recent data for {}'.format(event_info.event_name))
        update_start_dt = (price_info_status_qryset[0].mod_dt + timedelta(days=1)).strftime('%Y%m%d')
        price_info_status_model = price_info_status_qryset.first()
        price_info_status_model.mod_dt = datetime.date.today()
        price_info_status_model.save()
        info_update_yn = True
    # 해당 종목에 대해서 데이터 DELETE를 하고 다시 INSERT 해야하느 경우 - 앱내 DI로 업데이트하는 경우는 없고, 수동으로 DI로 변경필요.
    # 근데 UD은 업데이트하고 난 상태를 말하지만, DI는 업데이트 되어야하는 상태를 말하므로 혼동이 올수 있음... 사용다시 하게된다면 개선 필요.
    elif price_info_status_qryset.first().update_type == 'DI':
        print('update_stock_price : delete&insert for {}'.format(event_info.event_name))
        update_start_dt = stock_price_init_start_dt
        prev_stock_price_qryset = StockPrice.objects.filter(stock_event_id=event_info.stock_event_id)
        prev_stock_price_qryset.delete()
        price_info_status_model = price_info_status_qryset.first()
        price_info_status_model.mod_dt = datetime.date.today()
        price_info_status_model.update_type = 'UD'
        price_info_status_model.save()
        info_del_ins_yn = True

    if info_none_yn or info_update_yn or info_del_ins_yn:
        # price_info_df = stock.get_market_ohlcv_by_date(update_start_dt, today, event_info.event_code)
        price_info_df = wrap.get_market_ohlcv_by_date(update_start_dt, today, event_info.event_code)
        price_info_df = price_info_df.reset_index()
        price_info_df.rename(
            columns={'날짜': 'date', '시가': 'open', '종가': 'close', '거래량': 'volume', '고가': 'high', '저가': 'low',
                     '거래대금': 'value', '등락률': 'up_down_rate'},
            inplace=True)
        with transaction.atomic():
            for item in price_info_df.to_dict('records'):
                # if StockPrice.objects.filter(date=item['date']).filter(event_code=event_info.event_code).count() < 1:
                entry = StockPrice(**item)
                entry.event_code = event_info.event_code
                entry.stock_event_id = event_info.stock_event_id
                entry.save()
    else:
        print("update_stock_price : doesn't have to update. last modify date is {}"
              .format(price_info_status_qryset.first().mod_dt))


def update_event_info(start_date_str):
    '''
    전체 주식종목정보 업데이트
    :param start_date_str: 시뮬레이션 시작날짜 입력값
    :return:
    '''
    event_info_status_qryset = StockInfoUpdateStatus.objects.filter(table_type='E')
    # print('event_info_status={}'.format(event_info_status))
    # print('event_info_status count={}'.format(event_info_status.count()))
    # print('current time={}'.format(datetime.datetime.now()))
    if event_info_status_qryset.count() != 0:
        print('update_event_info : last mod date = {}'.format(event_info_status_qryset.first().mod_dt))
        print('update_event_info : date substract result = ',
              datetime.date.today() - event_info_status_qryset.first().mod_dt)
    if event_info_status_qryset.count() == 0 or (datetime.date.today() - event_info_status_qryset.first().mod_dt) \
            >= timedelta(days=stockConfig.EVENT_INFO_UPDATE_PERIOD):
        whole_code_df = wrap.get_market_ticker_and_name(date=start_date_str, market='ALL')
        whole_code_df = [{'event_code': k, 'event_name': v} for k, v in whole_code_df.iteritems()]
        # 종목코드가 변경되는 경우, 상장폐지 되는 경우, 신규상장되는 경우를 고려하여 업데이트 쿼리 작성 필요.
        with transaction.atomic():
            for item in whole_code_df:
                entry = StockEvent(**item)
                entry.save()
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
    high_list = []
    low_list = []
    date_list = []
    volume_list = []

    gui_ohlc = []
    gui_volume = []
    gui_whole = []
    print('make chart data : stocks = {}'.format(stocks))
    for stock in stocks:
        # time_tuple = strptime(str(stock.date), '%Y-%m-%d')
        # utc_now = mktime(time_tuple) * 1000
        # gui_whole.append([utc_now, stock.open, stock.high, stock.low, stock.close, stock.volume])
        open_list.append(stock.open)
        close_list.append(stock.close)
        high_list.append(stock.high)
        low_list.append(stock.low)
        date_list.append(stock.date)
        volume_list.append(stock.volume)

    # template = dict(
    #     layout=go.Layout(title_font=dict(family="plotly_dark", size=24))
    # )

    # Create figure with secondary y-axis
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.3, subplot_titles=('OHLC', 'Volume'),
                        row_width=[0.2, 0.7])

    # include candlestick with rangeselector
    fig.add_trace(go.Candlestick(x=date_list,
                                 open=open_list, high=high_list,
                                 low=low_list, close=close_list, increasing_line_color='skyblue',
                                 decreasing_line_color='gray', increasing_fillcolor='skyblue',
                                 decreasing_fillcolor='gray'), row=1, col=1)

    # include a go.Bar trace for volumes
    fig.add_trace(go.Bar(x=date_list, y=volume_list, marker_color='steelblue'), row=2, col=1)
    fig.update_layout(title=event_name,
                      template="plotly_white")

    fig.update_xaxes(
        title_text='Date',
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=1, label='1M', step='month', stepmode='backward'),
                dict(count=3, label='3M', step='month', stepmode='backward'),
                dict(count=6, label='6M', step='month', stepmode='backward'),
                dict(count=1, label='YTD', step='year', stepmode='todate'),
                dict(count=1, label='1Y', step='year', stepmode='backward'),
                dict(step='all')])))

    # fig.update_yaxes(autorange=True)
    # fig.layout.yaxis.update(autorange=True, fixedrange=False)

    # def zoom(layout, xrange):
    #     in_view_high = high_list[fig.layout.xaxis.range[0]:fig.layout.xaxis.range[1]]
    #     in_view_low = high_list[fig.layout.xaxis.range[0]:fig.layout.xaxis.range[1]]
    #     fig.layout.yaxis.range = [min(in_view_low) - 10, max(in_view_high) + 10]
    #
    # fig.layout.on_change(zoom, 'xaxis.range')

    graph = fig.to_html(full_html=False, default_height='150%')

    # Test
    #
    # trace = go.Scatter(x=date_list,
    #                    y=high_list)
    #
    # data = [trace]
    # layout = dict(
    #     title='Time series with range slider and selectors',
    #     xaxis=dict(
    #         rangeselector=dict(
    #             buttons=list([
    #                 dict(count=1,
    #                      label='1m',
    #                      step='month',
    #                      stepmode='backward'),
    #                 dict(count=6,
    #                      label='6m',
    #                      step='month',
    #                      stepmode='backward'),
    #                 dict(count=1,
    #                      label='YTD',
    #                      step='year',
    #                      stepmode='todate'),
    #                 dict(count=1,
    #                      label='1y',
    #                      step='year',
    #                      stepmode='backward'),
    #                 dict(step='all')
    #             ])
    #         ),
    #         rangeslider=dict(
    #             visible=True
    #         ),
    #         type='date'
    #     )
    # )
    #
    # fig_test = go.FigureWidget(data=data, layout=layout)
    #
    # def zoom(layout, xrange):
    #     in_view = high_list[fig.layout.xaxis.range[0]:fig.layout.xaxis.range[1]]
    #     fig.layout.yaxis.range = [min(in_view) - 2, max(in_view) + 2]
    #     print(in_view)
    #
    # fig_test.layout.on_change(zoom, 'xaxis.range')
    #
    # graph_test = fig_test.to_html(full_html=False, default_height='150%')

    return graph
