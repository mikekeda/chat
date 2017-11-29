import datetime
import json

from celery import Celery, shared_task
from chatterbot import ChatBot

from channels import Group

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings

from .models import Profile, Message

app = Celery('chat')

User = get_user_model()

chatbot = ChatBot(**settings.CHATTERBOT)


@app.task
def update_user_statuses():
    # Chat bot is always online.
    now = datetime.datetime.now()
    cache.set('seen_chatbot', now, settings.USER_ONLINE_TIMEOUT)

    Group('users').send({
        'text': json.dumps(Profile.get_online_users())
    })


@shared_task
def chatbot_response(thread_id, text):
    chatbot_user = User.objects.get(username='chatbot')

    response = chatbot.get_response(text)

    Message(
        thread_id=thread_id,
        user=chatbot_user,
        text=response
    ).save()
