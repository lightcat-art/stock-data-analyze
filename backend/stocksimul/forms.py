from django import forms
from .models import StockSimulParam


class StockSimulParamForm(forms.ModelForm):
    class Meta:
        model = StockSimulParam
        fields = ('event_name', 'start_date', 'days')
        # help_texts = {'event_name':('종목'),}
        labels = {'event_name':('종목'), 'start_date':('시작일자'),'days':('기간')}
