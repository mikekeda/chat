import datetime

import langid
from asgiref.sync import async_to_sync
from celery import Celery, shared_task
from channels.layers import get_channel_layer
from chatterbot import ChatBot
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache

from core.models import Message, Profile

app = Celery("chat")

channel_layer = get_channel_layer()
User = get_user_model()

chatbot = None  # lazy initialization due to a bug with Django 3.1.7
langid.set_languages([code for code, _ in settings.LANGUAGES])


@app.task
def update_user_statuses() -> None:
    """ Task to update user online statuses via websockets. """
    # Chat bot is always online.
    now = datetime.datetime.now()
    cache.set("seen_chatbot", now, settings.USER_ONLINE_TIMEOUT)

    async_to_sync(channel_layer.group_send)(
        "users", {"type": "users.update", "content": Profile.get_online_users()}
    )


@shared_task
def chatbot_response(thread_id: int, text: str) -> None:
    """ Task to send a response from Chatbot. """
    global chatbot  # lazy initialization due to a bug with Django 3.1.7

    if chatbot is None:
        chatbot = ChatBot(**settings.CHATTERBOT)

    chatbot_user = User.objects.get(username="chatbot")

    response = str(chatbot.get_response(text))

    message = Message(thread_id=thread_id, user=chatbot_user, text=response)
    message.lang, _ = langid.classify(message.text)
    message.save()
