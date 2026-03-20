import datetime

import langid
from asgiref.sync import async_to_sync
from celery import Celery, shared_task
from channels.layers import get_channel_layer

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from openai import OpenAI

openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)

from core.models import Message, Profile

app = Celery("chat")

channel_layer = get_channel_layer()
User = get_user_model()

langid.set_languages([code for code, _ in settings.LANGUAGES])



@app.task
def update_user_statuses() -> None:
    """Task to update user online statuses via websockets."""
    # Chat bot is always online.
    now = datetime.datetime.now()
    cache.set("seen_ChatGPT", now, settings.USER_ONLINE_TIMEOUT)

    async_to_sync(channel_layer.group_send)(
        "users", {"type": "users.update", "content": Profile.get_online_users()}
    )


@shared_task
def chat_gpt_response(thread_id: int) -> None:
    """Task to send a response from ChatGPT."""
    chat_gpt_user = User.objects.get(username="ChatGPT")
    messages = (
        Message.objects.select_related("user")
        .filter(thread_id=thread_id)
        .order_by("date")[:20]
    )
    response = openai_client.completions.create(
        model="gpt-5.4-mini",
        prompt="".join(
            [f"{message.user.username}: {message.text}\n" for message in messages]
            + [f"{chat_gpt_user.username}: "]
        ),
        temperature=0.9,
        max_tokens=150,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0.6,
        stop=["\n"]
        + [f"{user.username}: " for user in (messages[0].user, chat_gpt_user)],
    )
    answer = response.choices[0].text

    message = Message(thread_id=thread_id, user=chat_gpt_user, text=answer)
    message.lang, _ = langid.classify(message.text)
    message.save()
