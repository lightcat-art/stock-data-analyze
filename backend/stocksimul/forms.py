from django import forms
from .models import SimulParam


class StockSimulParamForm(forms.ModelForm):
    class Meta:
        model = SimulParam
        fields = ('event_name', 'start_date', 'days')
        # help_texts = {'event_name':('종목'),}
        labels = {'event_name': ('종목'), 'start_date': ('시작일자'), 'days': ('기간')}
        widgets = {
            'days': forms.NumberInput(attrs={
                'class': 'form-control chart_param',
                # 'style': 'width:150px',
                'placeholder': '조회기간 입력',
                'id': 'param-days'
            }),
            'start_date': forms.DateInput(attrs={'class': 'form-control chart_param_date',
                                                 'placeholder': 'Select a date',
                                                 'type': 'date',
                                                 'id': 'param-start-date'
                                                 # 'style': 'width:150px',
                                                 }),
        }
