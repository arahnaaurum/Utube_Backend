from .models import *
from rest_framework import serializers

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
       model = CustomUser
       fields = ['id', 'username', 'email', 'phone']


class AuthorSerializer(serializers.HyperlinkedModelSerializer):
    subscribed_to = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
       model = Author
       fields = ['id', 'identity', 'is_banned', 'subscribed_to']


class SubscriptionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
       model = Subscription
       fields = ['id', 'subscriber', 'author']


class VideoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
       model = Video
       fields = ['id', 'author', 'time_creation', 'title', 'description', 'file', 'hashtags']


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
       model = Comment
       fields = ['id', 'author', 'time_creation', 'video', 'text']


class LikeSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
       model = Like
       fields = ['id', 'author', 'time_creation', 'video']