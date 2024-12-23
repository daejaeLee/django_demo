# board/urls.py

from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('', views.mypage, name='mypage'),
    path('pwchange', views.pwchange, name='pwchange')
]