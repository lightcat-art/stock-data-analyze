from datetime import datetime, timedelta

from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .analyze.core import Core
from .forms import StockSimulParamForm
from .models import StockSimulParam


def stock_simul_param(request):
    if request.method == "POST":
        form = StockSimulParamForm(request.POST)
        if form.is_valid():  # 모든 필드에 값이 있어야 하고, 잘못된 값이 있다면 저장되지 않도록 체크.
            simul_param = form.save(commit=False)  # 폼을 저장하지만, 바로 모델에 저장하지 않도록 commit옵션 False
            simul_param.save()
            return redirect('stock_simul_result',pk=simul_param.pk)
    else:
        form = StockSimulParamForm()
    return render(request, 'stocksimul/stock_simul_param.html', {'form': form})


def stock_simul_result(request, pk):
    simul_param = get_object_or_404(StockSimulParam, pk=pk)
    print(simul_param.start_date)
    print(simul_param.days)
    end_date = (simul_param.start_date + timedelta(days=simul_param.days)).strftime('%Y%m%d')
    start_date = simul_param.start_date.strftime('%Y%m%d')
    print(start_date)
    print(end_date)
    Core().analyze('005930',start_date, end_date)
    return render(request, 'stocksimul/stock_simul_result.html', {'simul_param':simul_param})
