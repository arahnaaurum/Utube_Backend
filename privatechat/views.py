from django.shortcuts import render
from django.contrib.auth import get_user_model
from utube_app.models import *

# User = get_user_model()

def userlist(request):
    return render (request, 'userlist.html', {})

def privatechat(request, id):
    # user_obj = User.objects.get(id=id)
    user_obj = CustomUser.objects.get(id=id)
    return render (request, 'privatechat.html', context = {'user':user_obj})