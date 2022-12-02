from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.parsers import JSONParser
from django.contrib.auth.decorators import login_required
from .models import *
from .serializers import *

User = get_user_model()


def userlist(request):
    return render (request, 'userlist.html', {})

@login_required
def privatechat(request, id):
    user_obj = User.objects.get(id=id)
    # user_obj = CustomUser.objects.get(id=id)
    return render (request, 'privatechat.html', context = {'user':user_obj})


class PrivateMessageViewset(viewsets.ModelViewSet):
    queryset = PrivateMessage.objects.all()
    parser_classes = [JSONParser]
    serializer_class = PrivateMessageSerializer

    def get_queryset(self):
        queryset = PrivateMessage.objects.all()
        chat_id = self.request.query_params.get('chat', None)
        if chat_id is not None:
            queryset = PrivateMessage.objects.filter(chatId=chat_id)
        return queryset
