from django.db import models


class PublicChat(models.Model):
    name = models.CharField(max_length=200, null=False, primary_key=True, unique=True)

    def __str__(self):
        return self.name