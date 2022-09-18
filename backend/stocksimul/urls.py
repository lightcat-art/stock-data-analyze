from django.urls import path
from . import views


urlpatterns = [
    path('', views.stock_simul, name='post_list'),
]