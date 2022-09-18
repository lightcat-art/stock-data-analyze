from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .forms import StockSimulParamForm


def stock_simul_param(request):
    if request.method == "POST":
        form = StockSimulParamForm(request.POST)
        if form.is_valid():  # 모든 필드에 값이 있어야 하고, 잘못된 값이 있다면 저장되지 않도록 체크.
            stock = form.save(commit=False)  # 폼을 저장하지만, 바로 모델에 저장하지 않도록 commit옵션 False
            event_name = stock.event_name
            start_date = stock.start_date
            return redirect('stock_simul_result')
    else:
        form = StockSimulParamForm()
    return render(request, 'stocksimul/stock_simul_param.html', {'form': form})


def stock_simul_result(request):
    return render(request, 'stocksimul/stock_simul_result.html')
