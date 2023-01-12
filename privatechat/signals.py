from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import PrivateMessage
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from webpush import send_user_notification

User = get_user_model()

@receiver(post_save, sender=PrivateMessage)
def notify_by_push(sender, instance, created, **kwargs):
    recepiet_id = instance.recepient
    head = 'New message in private chat'
    body = instance.text
    payload = {'head': head, 'body': body}
    # user = get_object_or_404(User, pk=recepient_id)
    user = User.objects.get(id=recepiet_id)
    send_user_notification(user=user, payload=payload, ttl=1000)