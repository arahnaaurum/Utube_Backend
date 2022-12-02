from django.urls import path
from .views import *
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', personalView),
    path('login/', user_login, name='login'),
]