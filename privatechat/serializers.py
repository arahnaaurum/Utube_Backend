from .models import *
from rest_framework import serializers


class PrivateMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PrivateMessage
        fields = ['id', 'chatId', 'author', 'recepient', 'time_creation', 'text', 'isRead']
