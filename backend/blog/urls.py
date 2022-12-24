from django.urls import path
from . import views


urlpatterns = [
    # post_list라는 view를 루트 URL에 할당
    # 루트 웹사이트 주소로 들어왔을때 views.post_list를 보여주게 됨
    # path('post/', views.post_list, name='post_list'),
    # path('post/<int:pk>/', views.post_detail, name='post_detail'),
    # path('post/new',views.post_new, name='post_new'),
    # path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
]
