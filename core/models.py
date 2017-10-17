import datetime

from django.conf import settings
from django.db import models
from django.core.cache import cache
from channels.binding.websockets import WebsocketBinding


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, related_name='profile')
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/no-avatar.png'
    )

    def last_seen(self):
        return cache.get('seen_%s' % self.user.username)

    def online(self):
        if self.last_seen():
            now = datetime.datetime.now()
            return now < self.last_seen() + datetime.timedelta(
                seconds=settings.USER_ONLINE_TIMEOUT
            )

        return False

    def __str__(self):
        return u'%s' % (
            self.user.username,
        )


class Thread(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='threads'
    )
    last_message = models.DateTimeField(null=True)

    def __str__(self):
        return u'%s' % (
            self.name,
        )


class UnreadThread(models.Model):
    thread = models.ForeignKey(Thread)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='unread_thread'
    )
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return u'%s:%s' % (
            self.thread.name,
            self.user.username,
        )


class Message(models.Model):
    thread = models.ForeignKey(Thread, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.thread.last_message = datetime.datetime.now()
        self.thread.save()
        super(Message, self).save(force_insert=False, force_update=False,
                                  using=None, update_fields=None)

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
