import json
from channels import Group
from channels.auth import channel_session_user, channel_session_user_from_http
from channels.generic.websockets import WebsocketDemultiplexer

from .models import Thread, Message, MessageBinding


@channel_session_user_from_http
def ws_connect(message):
    Group('users').add(message.reply_channel)
    Group('users').send({
        'text': json.dumps({
            'username': message.user.username,
            'is_logged_in': True
        })
    })


@channel_session_user
def ws_disconnect(message):
    Group('users').send({
        'text': json.dumps({
            'username': message.user.username,
            'is_logged_in': False
        })
    })
    # for thread in message.channel_session['thread']:
    #     Group("thread-%s" % thread).discard(message.reply_channel)
    Group('users').discard(message.reply_channel)


class WsThread(WebsocketDemultiplexer):
    http_user = True

    consumers = {
        'messages': MessageBinding.consumer,
    }

    def connection_groups(self, thread):
        if Thread.objects.filter(pk=thread, users=self.message.user):
            return ['thread-%s' % thread]
        return []

    def receive(self, content, **kwargs):
        message = Message(thread_id=int(kwargs.get('thread')), user=self.message.user, text=content['text'])
        if message.thread.users.filter(pk=message.user.pk):
            message.save()
