from .models import *
from rest_framework import serializers


class PublicChatSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PublicChat
        fields = ['name']
