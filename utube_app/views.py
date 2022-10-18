from django.shortcuts import render
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from .models import *
from .serializers import *
from .search import search_video


class HomeView(TemplateView):
    template_name = 'flatpages/home.html'

class PersonalView(LoginRequiredMixin, TemplateView):
    template_name = 'flatpages/personal.html'

# информация о юзерах доступна только админу
class UserViewset(viewsets.ModelViewSet):
   queryset = CustomUser.objects.all()
   serializer_class = UserSerializer
   permission_classes = [permissions.IsAdminUser]


# создание авторского аккаунта и подписка д.б. доступна только зарегистрированным и авторизованным пользователям
class AuthorViewset(viewsets.ModelViewSet):
   queryset = Author.objects.all()
   serializer_class = AuthorSerializer
   permission_classes = [permissions.IsAuthenticated]

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
      return Response({"message": "Update request not allowed"})

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
   permission_classes = [permissions.IsAuthenticated]

   def update(self, request, *args, **kwargs):
      return Response({"message": "Update request not allowed"})

   def destroy(self, request, *args, **kwargs):
      subscription = self.get_object()
      logged_user = request.user
      if (logged_user == subscription.subscriber.identity):
         subscription.delete()
         response_message={"message": "Subscription has been deleted"}
      else:
         response_message = {"message": "Delete request not allowed"}
      return Response(response_message)


# видео, лайки, комменты доступны для просмотра всем, для записи - только авторизованным юзерам
class VideoViewset(viewsets.ModelViewSet):
   queryset = Video.objects.all()
   serializer_class = VideoSerializer
   permission_classes = [permissions.IsAuthenticatedOrReadOnly]

   def get_queryset(self):
      queryset = Video.objects.all()
      query = self.request.query_params.get('query', None)
      author_id = self.request.query_params.get('author_id', None)
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

   def destroy(self, request, *args, **kwargs):
      video = self.get_object()
      logged_user = request.user
      if (logged_user == video.author.identity):
         video.delete()
         response_message={"message": "Video has been deleted"}
      else:
         response_message = {"message": "Delete request not allowed"}
      return Response(response_message)


class CommentViewset(viewsets.ModelViewSet):
   queryset = Comment.objects.all()
   serializer_class = CommentSerializer
   permission_classes = [permissions.IsAuthenticatedOrReadOnly]

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

   def destroy(self, request, *args, **kwargs):
      comment = self.get_object()
      logged_user = request.user
      if (logged_user == comment.author.identity):
         comment.delete()
         response_message={"message": "Comment has been deleted"}
      else:
         response_message = {"message": "Delete request not allowed"}
      return Response(response_message)


class LikeViewset(viewsets.ModelViewSet):
   queryset = Like.objects.all()
   serializer_class = LikeSerializer
   permission_classes = [permissions.IsAuthenticatedOrReadOnly]

   def get_queryset(self):
      queryset = Like.objects.all()
      author_id = self.request.query_params.get('author_id', None)
      video_id = self.request.query_params.get('video_id', None)
      if author_id is not None:
         queryset = Like.objects.filter(author_id=author_id)
      if video_id is not None:
         queryset = Like.objects.filter(video_id=video_id)
      return queryset

   def update(self, request, *args, **kwargs):
      return Response({"message": "Update request not allowed"})

   def destroy(self, request, *args, **kwargs):
      like = self.get_object()
      logged_user = request.user
      if (logged_user == like.author.identity):
         like.delete()
         response_message={"message": "Like has been deleted"}
      else:
         response_message = {"message": "Delete request not allowed"}
      return Response(response_message)