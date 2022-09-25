from datetime import timedelta
from time import strptime, mktime
import json
from django.db import transaction

from django.shortcuts import render, get_object_or_404, redirect

from .analyze.core import Core
from .forms import StockSimulParamForm
from .models import StockSimulParam
from .models import StockPrice
from pykrx.website.krx.market import wrap


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


@transaction.atomic
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

    whole_code = wrap.get_market_ticker_and_name(date=start_date, market='ALL')
    print(whole_code)
    whole_code = dict([(v, k) for k, v in whole_code.iteritems()])
    event_code = whole_code.get(event_name)
    print(event_code)

    code_df = Core().stock_graph(event_code, start_date, end_date)
    code_df = code_df.reset_index()
    code_df.rename(columns={'날짜': 'date', '시가': 'open', '종가': 'close', '거래량': 'volume', '고가': 'high', '저가': 'low'},
                   inplace=True)
    print(code_df)
    for item in code_df.to_dict('records'):
        # print(item)
        print(StockPrice.objects.filter(date=item['date']).filter(event_code=event_code))
        if StockPrice.objects.filter(date=item['date']).filter(event_code=event_code).count() < 1:
            entry = StockPrice(**item)
            entry.event_code = event_code
            entry.save()

    stocks = StockPrice.objects.filter(event_code=event_code).order_by('date')

    chart_data = make_chart_data(stocks, event_name)

    code_df_html = code_df.to_html()

    return render(request, 'stocksimul/stock_simul_result.html', {'code_df': code_df_html, 'chart_data':chart_data})


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
