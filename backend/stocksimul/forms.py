from django import forms
from .models import StockSimulParam


class StockSimulParamForm(forms.ModelForm):
    class Meta:
        model = StockSimulParam
        fields = ('event_name', 'start_date', 'days')
