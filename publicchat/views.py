from django.shortcuts import render
from requests import Response
from rest_framework import viewsets
from rest_framework.parsers import JSONParser
from django.contrib.auth.decorators import login_required
from .models import *
from .serializers import *


def index(request):
    return render(request, 'index.html', {})

@login_required
def room(request, room_name):
    return render(request, 'chatroom.html', {
        'room_name': room_name
    })


class PublicChatViewset(viewsets.ModelViewSet):
    queryset = PublicChat.objects.all()
    parser_classes = [JSONParser]
    serializer_class = PublicChatSerializer
