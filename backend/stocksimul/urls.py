from django.urls import path, include
from . import views
from rest_framework import routers
from .views import HealthCheckAPI

# router = routers.DefaultRouter()
# router.register('healthcheck', HealthCheckAPI)

urlpatterns = [
    # path('', views.stock_simul_param, name='stock_simul_param'),
    # path('stock/simul/result/<int:pk>/', views.stock_simul_result, name='stock_simul_result'),
    # path('stock/simul/result/<str:event_name>_<str:start_date_str>_<str:end_date_str>/', views.render_stock_simul_result, name='render_stock_simul_result'),
    # path('stock/simul/ajaxchartdata/', views.ajax_chart_data, name='ajax_chart_data'),
    # path('stock/simul/ajaxplotly_chartdata', views.ajax_plotly_chart_data, name='ajax_plotly_chart_data'),
    # path('', include(router.urls)),
    path('healthcheck', views.HealthCheckAPI, name='health_check')
]