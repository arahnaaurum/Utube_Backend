import json
from django.test import TestCase
from .serializers import *
from .models import *
from .search import search_video
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.request import Request
from django.core.files.uploadedfile import File, SimpleUploadedFile

class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        #Set up non-modified objects used by all test methods
        user = CustomUser.objects.create_user('Jane', 'jane@mail.com', phone = "12345")
        Author.objects.create(identity=user)

    # проверим, что автор наследует все поля кастомизированного юзера
    def test_username_is_inherited(self):
        author = Author.objects.get(id=1)
        username = author.identity.username
        self.assertEquals(username,'Jane')

    def test_email_is_inherited(self):
        author = Author.objects.get(id=1)
        email = author.identity.email
        self.assertEquals(email, 'jane@mail.com')

    def test_phone_is_inherited(self):
        author = Author.objects.get(id=1)
        phone = author.identity.phone
        self.assertEquals(phone,'12345')

    def test_is_banned_is_false(self):
        author = Author.objects.get(id=1)
        self.assertFalse(author.is_banned)

class VideoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user('Jane', 'jane@mail.com', phone = "12345")
        author = Author.objects.create(identity=user)
        Video.objects.create(author=author, title='Jaws', description='Very big shark', hashtags = ['shark', 'jaws'])

    def test_username_is_inherited(self):
        video = Video.objects.get(id=1)
        username = video.author.identity.username
        self.assertEquals(username,'Jane')

    def test_title_is_right(self):
        video = Video.objects.get(id=1)
        title = video.title
        self.assertEquals(title,'Jaws')

    def test_description_is_right(self):
        video = Video.objects.get(id=1)
        description = video.description
        self.assertEquals(description,'Very big shark')

    def test_search_by_description_works(self):
        video = Video.objects.get(description='Very big shark')
        self.assertEquals(video.id, 1)

    def test_search_by_one_hashtag_works(self):
        video = Video.objects.get(hashtags__contains=['shark'])
        self.assertEquals(video.id, 1)

    def test_search_by_many_hashtags_works(self):
        video = Video.objects.get(hashtags__contains=['shark', 'jaws'])
        self.assertEquals(video.id, 1)


class VideoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user('Jane', 'jane@mail.com', phone = "12345")
        author = Author.objects.create(identity=user)
        video = Video.objects.create(id=100, author=author, title='Jaws', description='Very big shark', hashtags = ['shark', 'jaws'])
        Comment.objects.create(author=author, video=video, text='LOL')

    def test_search_by_comments_text_works(self):
        comment = Comment.objects.get(text='LOL')
        video = comment.video
        self.assertEquals(video.id, 100)


class SearchMethodTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create_user('Jane', 'jane@mail.com', phone="12345")
        author = Author.objects.create(identity=user)
        video1 = Video.objects.create(id=1, author=author, title='Jaws', description='Very big shark',
                                      hashtags=['shark', 'jaws'])
        video2 = Video.objects.create(id=2, author=author, title='Saw', description='Very scary game',
                                      hashtags=['saw', 'game'])
        video3 = Video.objects.create(id=3, author=author, title='Jaws 2', description='Very big shark',
                                      hashtags=['shark', 'jaws', 'sequel'])
        video4 = Video.objects.create(id=4, author=author, title='Saw 2', description='Very scary game',
                                      hashtags=['saw', 'game', 'sequel'])
        comment1 = Comment.objects.create(author=author, video=video1, text='LOL')
        comment2 = Comment.objects.create(author=author, video=video2, text='Onono')
        comment3 = Comment.objects.create(author=author, video=video3, text='lol')
        comment4 = Comment.objects.create(author=author, video=video3, text='Onono')

    def test_search_by_description_works(self):
        video1 = Video.objects.get(id=1)
        video3 = Video.objects.get(id=3)
        list = search_video('shark');
        # search_video('very');
        self.assertEquals(list, [video1, video3])

    def test_search_by_hastag_works(self):
        video3 = Video.objects.get(id=3)
        video4 = Video.objects.get(id=4)
        list = search_video('sequel');
        # search_video('game');
        self.assertEquals(list, [video3, video4])

    def test_search_by_comments_works(self):
        video1 = Video.objects.get(id=1)
        video3 = Video.objects.get(id=3)
        list = search_video('lol');
        self.assertEquals(list, [video1, video3])


class CommentAPITest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user('Jane', 'jane@mail.com', phone="12345")
        self.author = Author.objects.create(identity=self.user)
        self.other_user = CustomUser.objects.create_user('Jon', 'jon@mail.com', phone="12345")
        self.other_author = Author.objects.create(identity=self.other_user)
        self.video5 = Video.objects.create(id=5, author=self.author, title='Jaws', file='',
                                           description='Very big shark', hashtags=['shark', 'jaws'])
        self.comment1 = Comment.objects.create(author=self.other_author, video=self.video5, text='LOL')
        self.comment2 = Comment.objects.create(author=self.author, video=self.video5, text='Onono')
        self.comment3 = Comment.objects.create(author=self.author, video=self.video5, text='Kek')
        self.comment4 = Comment.objects.create(author=self.author, video=self.video5, text='Hah')
        self.client.force_authenticate(user=self.user)

    def test_get_all_comments(self):
        response = self.client.get(reverse('comment-list'))
        comments = Comment.objects.all()
        # сравним количество объектов
        self.assertEqual(response.data['count'], len(comments))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_comment(self):
        response = self.client.get(reverse('comment-detail', kwargs={'pk': self.comment3.pk}))
        comment = Comment.objects.get(pk=self.comment3.pk)
        self.assertEqual(response.data['text'], comment.text)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_comment(self):
        serialized_comment = CommentSerializer(self.comment1, context={'request': None})
        data = serialized_comment.data
        response = self.client.post(reverse('comment-list'), data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_delete_comment(self):
        response = self.client.delete(
            reverse('comment-detail', kwargs={'pk': self.comment4.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_delete_other_users_comment(self):
        response = self.client.delete(
            reverse('comment-detail', kwargs={'pk': self.comment1.pk}))
        self.assertEqual(response.data['message'], "Delete request not allowed")


class VideoAPITests(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user('Jane', 'jane@mail.com', phone="12345")
        self.author = Author.objects.create(identity=self.user)
        self.other_user = CustomUser.objects.create_user('Jon', 'jon@mail.com', phone="12345")
        self.other_author = Author.objects.create(identity=self.other_user)
        self.video6 = Video.objects.create(id=6, author=self.author, title='Nightmare Before Christmas', file='../media/Kite.mp4',
                                           description='Songs', hashtags=['halloween', 'jack'])
        self.video7 = Video.objects.create(id=7, author=self.other_author, title='Jaws', file='../media/Kite.mp4',
                                           description='Very big shark', hashtags=['shark', 'jaws'])
        self.client.force_authenticate(user=self.user)

    def test_create_video(self):
        filename = 'Kite.mp4'
        file = File(open('media/Kite.mp4', 'rb'))
        uploaded_file = SimpleUploadedFile(filename, file.read(),
                                           content_type='multipart/form-data')
        data = {"id":6, "author":self.author.pk, "title":'Nightmare Before Christmas', "file":uploaded_file,
                                           "description":'Songs', "hashtags":'halloween'}
        response = self.client.post(reverse('video-list'), data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_all_videos(self):
        response = self.client.get(reverse('video-list'))
        videos = Video.objects.all()
        self.assertEqual(response.data['count'], len(videos))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_video(self):
        response = self.client.get(reverse('video-detail', kwargs={'pk': self.video6.pk}))
        video = Video.objects.get(pk=self.video6.pk)
        self.assertEqual(response.data['title'], video.title)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_video(self):
        response = self.client.delete(
            reverse('video-detail', kwargs={'pk': self.video6.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_delete_other_users_video(self):
        response = self.client.delete(reverse('video-detail', kwargs={'pk': self.video7.pk}))
        self.assertEqual(response.data['message'], "Delete request not allowed")


class LikeAPITest(APITestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user('Jane', 'jane@mail.com', phone="12345")
        self.author = Author.objects.create(identity=self.user)
        self.other_user = CustomUser.objects.create_user('Jon', 'jon@mail.com', phone="12345")
        self.other_author = Author.objects.create(identity=self.other_user)
        self.video8 = Video.objects.create(id=8, author=self.author, title='Jaws', file='',
                                           description='Very big shark', hashtags=['shark', 'jaws'])
        self.like1 = Like.objects.create(author=self.author, video=self.video8)
        self.like2 = Like.objects.create(author=self.other_author, video=self.video8)
        self.client.force_authenticate(user=self.user)

    def test_create_like(self):
        payload = {'author': self.author.pk, 'video': self.video8.pk, 'text':'kekeke'}
        response = self.client.post(reverse('like-list'), data=json.dumps(payload), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_get_all_likes(self):
        response = self.client.get(reverse('like-list'))
        likes = Like.objects.all()
        self.assertEqual(response.data['count'], len(likes))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_single_like(self):
        response = self.client.get(reverse('like-detail', kwargs={'pk': self.like1.pk}))
        like = Like.objects.get(pk=self.like1.pk)
        self.assertEqual(response.data['id'], like.id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_like(self):
        response = self.client.delete(reverse('like-detail', kwargs={'pk': self.like1.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_cannot_delete_other_users_like(self):
        response = self.client.delete(reverse('like-detail', kwargs={'pk': self.like2.pk}))
        self.assertEqual(response.data['message'], "Delete request not allowed")