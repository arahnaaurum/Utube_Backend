from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin

class HomeView(TemplateView):
    template_name = 'flatpages/home.html'

class PersonalView(LoginRequiredMixin, TemplateView):
    template_name = 'flatpages/personal.html'