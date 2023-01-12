import os
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Video, CustomUser
from django.contrib.auth import get_user_model
from webpush import send_user_notification
from twilio.rest import Client


User = get_user_model()

# push-уведомления при создании видео
@receiver(post_save, sender=Video)
def notify_by_push(sender, instance, created, **kwargs):
    head = f'New video: {instance.title}'
    body = instance.description
    payload = {'head': head, 'body': body}
    for user in User.objects.all():
        send_user_notification(user=user, payload=payload, ttl=1000)


# отправка смс через Twilio при регистрации нового юзера

# смс с простым приветствием через Twilio Messenger
# @receiver(post_save, sender=CustomUser)
# def notify_by_SMS(sender, instance, created, **kwargs):
#     account_sid = os.environ['TWILIO_ACCOUNT_SID'] # заменить на данные из аккаунта
#     auth_token = os.environ['TWILIO_AUTH_TOKEN'] # заменить на данные из аккаунта
#     client = Client(account_sid, auth_token)
#
#     message = client.messages \
#         .create(
#         body=f'Welcome to Utube, {instance.username}',
#         from_='+15017122661', # заменить на данные из аккаунта
#         # messaging_service_sid='MG9752274e9e519418a7406176694466fa',
#         to=f'{instance.phone}'
#     )


# смс с кодом подтверждения через Twilio Verify
# @receiver(post_save, sender=CustomUser)
# def verify_by_SMS(sender, instance, created, **kwargs):
#     account_sid = os.environ['TWILIO_ACCOUNT_SID']
#     auth_token = os.environ['TWILIO_AUTH_TOKEN']
#     client = Client(account_sid, auth_token)
#
#     заменить 'VAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' на VERIFICATION_SID
#     verification = client.verify \
#                          .v2 \
#                          .services('VAXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX') \
#                          .verifications \
#                          .create(to=f'{instance.phone}', channel='sms')

#     return verification.sid