from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.http import require_GET, require_POST
from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from webpush import send_user_notification
from django.conf import settings
import json


User = get_user_model()

@require_GET
def start(request):
# webpush_settings: This is assigned the value of the WEBPUSH_SETTINGS attribute from the settings configuration.
    webpush_settings = getattr(settings, 'WEBPUSH_SETTINGS', {})
# This gets the VAPID_PUBLIC_KEY value from the webpush_settings object to send to the client.
# This public key is checked against the private key to ensure that the client with the public key is permitted
# to receive push messages from the server.
    vapid_key = webpush_settings.get('VAPID_PUBLIC_KEY')
# user: This variable comes from the incoming request.
    user = request.user
# The render function will return an HTML file and a context object containing the current user and the server’s vapid public key.
    return render(request, 'start.html', {user: user, 'vapid_key': vapid_key})


@require_POST
@csrf_exempt
def send_push(request):
    try:
        body = request.body
        data = json.loads(body)

        if 'head' not in data or 'body' not in data or 'id' not in data:
            return JsonResponse(status=400, data={"message": "Invalid data format"})

        user_id = data['id']
        user = get_object_or_404(User, pk=user_id)
        payload = {'head': data['head'], 'body': data['body']}

        # send_user_notification function from the webpush library
        # User: The recipient
        # payload: The notification information, which includes the notification head and body.
        # ttl: The maximum time in seconds that the  notification  should  be stored if the user is offline.

        send_user_notification(user=user, payload=payload, ttl=1000)

        return JsonResponse(status=200, data={"message": "Web push successful"})
    except TypeError:
        return JsonResponse(status=500, data={"message": "An error occurred"})


