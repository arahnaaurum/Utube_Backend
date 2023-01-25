from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField

class CustomUser(AbstractUser):
    # кастомизированной модели юзера добавлено поле с номером телефона, запрашиваемое при регистрации
    phone = models.CharField(max_length=200, blank=True, null=True)
    phone_verified = models.BooleanField(default=False, null=True)

# чтобы избежать путаницы с моделью User, стандартный пользователь будет обозначен как "автор"
class Author(models.Model):
    identity = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    is_banned = models.BooleanField(default=False)
    subscribed_to = models.ManyToManyField("Author", through="Subscription")
    profile_pic = models.ImageField(null=True, blank=True)

    def __str__(self):
        return f'{self.identity.username}'


class Subscription(models.Model):
    subscriber = models.ForeignKey("Author", on_delete=models.CASCADE, related_name='subscriber')
    author = models.ForeignKey("Author", on_delete=models.CASCADE, related_name='subscribee')


class Video(models.Model):
    author = models.ForeignKey("Author", on_delete=models.CASCADE, related_name="copyright")
    time_creation = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=128)
    description = models.TextField(null=True)
    file = models.FileField()

    # при использовании PostgreSQL хэштеги можно также хранить в массиве, а не создавать отдельный класс/таблицу:
    # hashtags = ArrayField(models.CharField(max_length=20, blank=True), size=10, default= default_hashtags)

    hashtags = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.title}'


class Comment(models.Model):
    author = models.ForeignKey("Author", on_delete=models.CASCADE)
    time_creation = models.DateTimeField(auto_now_add=True)
    video = models.ForeignKey("Video", on_delete=models.CASCADE)
    text = models.TextField()


class Like(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    time_creation = models.DateTimeField(auto_now_add=True)
    video = models.ForeignKey("Video", on_delete=models.CASCADE)