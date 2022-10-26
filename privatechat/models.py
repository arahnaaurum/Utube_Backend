from django.db import models
from utube_app.models import Author

class PrivateMessage(models.Model):
    chatId = models.IntegerField(default=0)
    author = models.IntegerField()
    recepient = models.IntegerField()
    time_creation = models.DateTimeField(auto_now_add=True)
    text = models.TextField()
    isRead = models.BooleanField(default=False)