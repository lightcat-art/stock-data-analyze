from django.urls import path
from . import views


urlpatterns = [
    path('', views.stock_simul_param, name='stock_simul_param'),
    path('stock/simul/result/<int:pk>/', views.stock_simul_result, name='stock_simul_result'),
    path('stock/simul/ajaxchartdata/', views.ajax_chart_data, name='ajax_chart_data'),
]