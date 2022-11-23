import os
from twilio.rest import Client
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import BasicAuthentication

from rest_framework.response import Response
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser, JSONParser

from .models import *
from .serializers import *
from .search import search_video, search_video_by_subscription
from .forms import *
from rest_framework.decorators import api_view

from webpush import send_user_notification

@login_required(login_url='/accounts/login/')
def personalView(request):
   sms_form = SMSForm()
   # if request.method == 'POST':
   #    sms_form = SMSForm(request.POST)
      # if sms_form.is_valid():
      #    sms_code = form.cleaned_data['SMS_code']
      #    account_sid = os.environ['TWILIO_ACCOUNT_SID']
      #    auth_token = os.environ['TWILIO_AUTH_TOKEN']
      #    client = Client(account_sid, auth_token)
      #
      #    заменить 'VAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'на VERIFICATION_SID
      #
      #    verification_check = client.verify \
      #       .v2 \
      #       .services('VAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX') \
      #       .verification_checks \
      #       .create(to='+15017122661', code=f'{sms_code}')
      #
      #    if verification_check.status == "approved":
      #       user = CustomUser.objects.get(id=request.user.id)
      #       user.phone_verified = True
      #       user.save()
      #       return HttpResponseRedirect('/')

   try:
      author = Author.objects.get(identity=request.user.id)
   except:
      form = CreateAuthorForm()
      if request.method == 'POST':
         form = CreateAuthorForm(request.POST, request.FILES)
         if form.is_valid():
            profile_pic = form.cleaned_data['profile_pic']
            new_author = Author.objects.create(identity=request.user, profile_pic=profile_pic)
            new_author.save()
   else:
      form = AuthorForm(instance=author)
      if request.method == 'POST':
         form = AuthorForm(request.POST, request.FILES, instance=author)
         if form.is_valid():
            form.save()

   context = {'form':form, 'smsform':sms_form}
   return render(request, 'account/personal.html', context)


# информация о юзерах доступна только админу
class UserViewset(viewsets.ModelViewSet):
   queryset = CustomUser.objects.all()
   serializer_class = UserSerializer
   permission_classes = [permissions.IsAdminUser]


class AuthorViewset(viewsets.ModelViewSet):
   queryset = Author.objects.all()
   serializer_class = AuthorSerializer

   def get_queryset(self):
      queryset = Author.objects.all()
      user_id = self.request.query_params.get('user_id', None)
      if user_id is not None:
         queryset = Author.objects.filter(identity=user_id)
      return queryset

   def create(self, request, *args, **kwargs):
      author_data = request.data
      logged_user = request.user
      new_author = Author.objects.create(identity=logged_user)
      new_author.save()
      serializer_context = {
         'request': request,
      }
      serializer = AuthorSerializer(new_author, context=serializer_context)
      return Response(serializer.data)

   def update(self, request, *args, **kwargs):
      author = self.get_object()
      logged_user = request.user
      if (logged_user == author.identity):
         partial = kwargs.pop('partial', True)
         instance = self.get_object()
         serializer = self.get_serializer(instance, data=request.data, partial=partial)
         serializer.is_valid(raise_exception=True)
         self.perform_update(serializer)
         return Response(serializer.data)
      else:
         response_message = {"message": "Delete request not allowed"}
         return Response(response_message)

   def destroy(self, request, *args, **kwargs):
      author = self.get_object()
      logged_user = request.user
      if (logged_user == author.identity):
         author.delete()
         response_message={"message": "Author has been deleted"}
      else:
         response_message = {"message": "Delete request not allowed"}
      return Response(response_message)


class SubscriptionViewset(viewsets.ModelViewSet):
   queryset = Subscription.objects.all()
   serializer_class = SubscriptionSerializer
   # permission_classes = [permissions.IsAuthenticated]

   def get_queryset(self):
      queryset = Subscription.objects.all()
      subscriber = self.request.query_params.get('subscriber', None)
      author = self.request.query_params.get('author', None)
      if subscriber is not None:
         if author is not None:
            queryset = Subscription.objects.filter(subscriber=subscriber, author=author)
         else:
            queryset = Subscription.objects.filter(subscriber=subscriber)
      return queryset

   def update(self, request, *args, **kwargs):
      return Response({"message": "Update request not allowed"})

   # def destroy(self, request, *args, **kwargs):
   #    subscription = self.get_object()
   #    logged_user = request.user
   #    if (logged_user == subscription.subscriber.identity):
   #       subscription.delete()
   #       response_message={"message": "Subscription has been deleted"}
   #    else:
   #       response_message = {"message": "Delete request not allowed"}
   #    return Response(response_message)


class VideoViewset(viewsets.ModelViewSet):
   # parser_classes = [JSONParser, FileUploadParser, MultiPartParser, FormParser,]
   queryset = Video.objects.all()
   serializer_class = VideoSerializer
   # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

   # def create(self, request, *args, **kwargs):
   #    author_data = Author.objects.get(id=request.data['author'])
   #    title_data = request.data['title']
   #    description_data = request.data['description']
   #    hashtags_data = request.data['hashtags']
   #    video_obj = request.data['file']
   #
   #    new_video = Video.objects.create(author=author_data,
   #                                     title=title_data,
   #                                     description=description_data,
   #                                     file=video_obj,
   #                                     hashtags=hashtags_data)
   #    new_video.save()
   #    serializer_context = {
   #       'request': request,
   #    }
   #    serializer = VideoSerializer(new_video, context=serializer_context)
   #    return Response(serializer.data)

   def get_queryset(self):
      queryset = Video.objects.all()
      subscriber_id = self.request.query_params.get('subscriber_id', None)
      query = self.request.query_params.get('query', None)
      author_id = self.request.query_params.get('author_id', None)
      if subscriber_id is not None:
         queryset = search_video_by_subscription(subscriber_id)
      if query is not None:
         queryset = search_video(query)
      if author_id is not None:
         queryset = Video.objects.filter(author_id=author_id)
      return queryset

   def update(self, request, *args, **kwargs):
      partial = True
      instance = self.get_object()
      logged_user = request.user
      if (logged_user == instance.author.identity):
         serializer = self.get_serializer(instance, data=request.data, partial=partial)
         serializer.is_valid(raise_exception=True)
         self.perform_update(serializer)
         return Response(serializer.data)
      else:
         response_message = {"message": "Update request not allowed"}
         return Response(response_message)

   # def destroy(self, request, *args, **kwargs):
   #    video = self.get_object()
   #    logged_user = request.user
   #    if (logged_user == video.author.identity):
   #       video.delete()
   #       response_message={"message": "Video has been deleted"}
   #    else:
   #       response_message = {"message": "Delete request not allowed"}
   #    return Response(response_message)


class CommentViewset(viewsets.ModelViewSet):
   queryset = Comment.objects.all()
   serializer_class = CommentSerializer
   # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

   def get_queryset(self):
      queryset = Comment.objects.all()
      author_id = self.request.query_params.get('author_id', None)
      video_id = self.request.query_params.get('video_id', None)
      if author_id is not None:
         queryset = Comment.objects.filter(author_id=author_id)
      if video_id is not None:
         queryset = Comment.objects.filter(video_id=video_id)
      return queryset

   def update(self, request, *args, **kwargs):
      partial = True
      instance = self.get_object()
      logged_user = request.user
      if (logged_user == instance.author.identity):
         serializer = self.get_serializer(instance, data=request.data, partial=partial)
         serializer.is_valid(raise_exception=True)
         self.perform_update(serializer)
         return Response(serializer.data)
      else:
         response_message = {"message": "Update request not allowed"}
         return Response(response_message)

   # def destroy(self, request, *args, **kwargs):
   #    comment = self.get_object()
   #    logged_user = request.user
   #    if (logged_user == comment.author.identity):
   #       comment.delete()
   #       response_message={"message": "Comment has been deleted"}
   #    else:
   #       response_message = {"message": "Delete request not allowed"}
   #    return Response(response_message)


class LikeViewset(viewsets.ModelViewSet):
   queryset = Like.objects.all()
   serializer_class = LikeSerializer
   # permission_classes = [permissions.IsAuthenticatedOrReadOnly]

   def get_queryset(self):
      queryset = Like.objects.all()
      author_id = self.request.query_params.get('author_id', None)
      video_id = self.request.query_params.get('video_id', None)
      if (author_id is not None) and (video_id is not None):
         queryset = Like.objects.filter(author_id=author_id, video_id=video_id)
      elif video_id is not None:
         queryset = Like.objects.filter(video_id=video_id)
      elif author_id is not None:
         queryset = Like.objects.filter(author_id=author_id)
      return queryset

   def update(self, request, *args, **kwargs):
      return Response({"message": "Update request not allowed"})

   # def destroy(self, request, *args, **kwargs):
   #    like = self.get_object()
   #    logged_user = request.user
   #    if (logged_user == like.author.identity):
   #       like.delete()
   #       response_message={"message": "Like has been deleted"}
   #    else:
   #       response_message = {"message": "Delete request not allowed"}
   #    return Response(response_message)


class CurrentViewset(viewsets.ModelViewSet):
   authentication_classes = [BasicAuthentication]
   permission_classes = [IsAuthenticated]
   queryset = CustomUser.objects.all()
   serializer_class = UserSerializer

   def get_queryset(self):
      queryset = CustomUser.objects.all()
      user_id = self.request.user.id
      queryset = CustomUser.objects.filter(id = user_id)
      return queryset