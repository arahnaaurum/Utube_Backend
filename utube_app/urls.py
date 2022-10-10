from django.urls import path
from .views import *
from django.contrib.auth.views import LoginView, LogoutView

urlpatterns = [
    path('', HomeView.as_view()),
    path('personal/', PersonalView.as_view()),
]