import datetime

from django.conf import settings
from django.db import models
from django.core.cache import cache
from django.urls import reverse
from channels.binding.websockets import WebsocketBinding


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        related_name='profile',
        on_delete=models.CASCADE
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        default='avatars/no-avatar.png'
    )
    lon = models.FloatField(blank=True, null=True)
    lat = models.FloatField(blank=True, null=True)

    def preview(self):
        return '<img src="{}{}" width="150" height="150" />'.format(
            settings.MEDIA_URL,
            self.avatar
        )

    preview.short_description = 'Avatar preview'
    preview.allow_tags = True

    def online(self):
        """Check if user is online (if Redis still has key 'seen_username')."""
        return cache.get('seen_{}'.format(self.user.username))

    @staticmethod
    def get_online_users():
        """Return a list of usernames of online users."""
        return [
            key[len('seen_'):]
            for key in cache.keys('seen_*')  # pattern is 'seen_username'
        ]

    def __str__(self):
        return self.user.username


class Thread(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='threads'
    )
    last_message = models.DateTimeField(null=True)

    def link_to_thread(self):
        return '<a href="{}">{}</a>'.format(
            reverse('core:thread', kwargs={'thread_id': self.pk}),
            self.name
        )

    link_to_thread.short_description = 'Link to thread'
    link_to_thread.allow_tags = True

    def __str__(self):
        return self.name


class UnreadThread(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='unread_thread',
        on_delete=models.CASCADE
    )
    date = models.DateTimeField(auto_now_add=True)

    def link_to_thread(self):
        return '<a href="{}">{}</a>'.format(
            reverse('core:thread', kwargs={'thread_id': self.thread.pk}),
            self.thread.name
        )

    link_to_thread.short_description = 'Link to thread'
    link_to_thread.allow_tags = True

    def __str__(self):
        return '{}: {}'.format(self.thread.name, self.user.username)


class Message(models.Model):
    thread = models.ForeignKey(
        Thread,
        related_name='messages',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    text = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def link_to_thread(self):
        return '<a href="{}">{}</a>'.format(
            reverse('core:thread', kwargs={'thread_id': self.thread.pk}),
            self.thread.name
        )

    link_to_thread.short_description = 'Link to thread'
    link_to_thread.allow_tags = True

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.thread.last_message = datetime.datetime.now()
        self.thread.save()
        super(Message, self).save(force_insert=False, force_update=False,
                                  using=None, update_fields=None)

    def __str__(self):
        return '{}: {}'.format(self.user.username, self.text[:100])


class MessageBinding(WebsocketBinding):
    model = Message
    stream = 'messages'
    fields = ['__all__']

    @classmethod
    def group_names(cls, instance):
        """
        Returns the iterable of group names to send the object to based on the
        instance and action performed on it.
        """
        return ['thread-{}'.format(instance.thread.pk)]

    def has_permission(self, user, action, pk):
        """
        Return True if the user can do action to the pk, False if not.
        User may be AnonymousUser if no auth hooked up/they're not logged in.
        Action is one of "create", "delete", "update".
        """
        if action == 'create':
            return True

        return user.is_superuser
