from django.test import TestCase
from .models import *
from .search import search_video

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