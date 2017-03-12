from django.conf import settings
from django.db import models
from datetime import datetime
from channels.binding.websockets import WebsocketBinding


class LoggedInUser(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='logged_in_user')

    def __str__(self):
        return u'%s' % (
            self.user.username,
        )


class Thread(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='threads')
    last_message = models.DateTimeField(null=True)

    def __str__(self):
        return u'%s' % (
            self.name,
        )


class Message(models.Model):
    thread = models.ForeignKey(Thread, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.thread.last_message = datetime.now()
        self.thread.save()
        super(Message, self).save(*args, **kwargs)

    def __str__(self):
        return u'%s: %s' % (
            self.user.username,
            self.text[:100],
        )


class MessageBinding(WebsocketBinding):
    model = Message
    stream = 'messages'
    fields = ['__all__']

    @classmethod
    def group_names(cls, instance):
        return ['thread-%s' % instance.thread.pk]

    def has_permission(self, user, action, pk):
        return user in self.users
