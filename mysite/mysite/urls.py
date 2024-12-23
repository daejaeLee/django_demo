# mysite/urls.py

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include('home.urls', namespace='home')),
    path('admin/', admin.site.urls),
    path('accounts/', include("accounts.urls", namespace='accounts')),
    path('board/', include('board.urls', namespace='board')),
    path('mypage/', include('user.urls', namespace='user'))
]       