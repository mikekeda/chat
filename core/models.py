import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models
from django.urls import reverse
from django.utils.html import format_html
from channels.binding.websockets import WebsocketBinding

User = get_user_model()


def get_username_by_uid(obj):
    """ Helper function to get user username by user id. """
    # Try to get username from the cache to avoid unneeded queries,
    # pattern is 'username_by_id_<user_id>'
    username = cache.get('username_by_id_{}'.format(obj.user_id))
    if not username:
        # We don't have the username - get username and set it to the cache.
        username = obj.user.username
        cache.set(
            'username_by_id_{}'.format(obj.user_id),
            username,
            settings.USER_ONLINE_TIMEOUT
        )

    return username


class Profile(models.Model):
    user = models.OneToOneField(
        User,
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
        return format_html(
            '<img src="{}{}" width="150" height="150" />',
            settings.MEDIA_URL,
            self.avatar
        )

    preview.short_description = 'Avatar preview'

    def location(self):
        """Show user location on a map."""
        return format_html(
            '<img src="{}"/>',
            'https://maps.googleapis.com/maps/api/staticmap?'
            'zoom=5&size=600x300&maptype=roadmap'
            '&markers=color:red%7Clabel:C%7C{},{}&key={}'.format(
                self.lat,
                self.lon,
                settings.GOOGLE_MAP_API_KEY
            )
        ) if self.lat and self.lon else 'No location available'

    def online(self):
        """Check if user is online (if Redis still has key 'seen_username')."""
        return cache.get('seen_{}'.format(get_username_by_uid(self)))

    @staticmethod
    def get_online_users():
        """Return a list of usernames of online users."""
        return [
            key[len('seen_'):]
            for key in cache.keys('seen_*')  # pattern is 'seen_username'
        ]

    def __str__(self):
        return get_username_by_uid(self)


class Thread(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(User, related_name='threads')
    last_message = models.DateTimeField(null=True)

    def link_to_thread(self):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('core:thread', kwargs={'thread_id': self.pk}),
            self.name
        )

    link_to_thread.short_description = 'Link to thread'

    def __str__(self):
        return self.name


class UnreadThread(models.Model):
    thread = models.ForeignKey(Thread, on_delete=models.CASCADE)
    user = models.ForeignKey(
        User,
        related_name='unread_thread',
        on_delete=models.CASCADE
    )
    date = models.DateTimeField(auto_now_add=True)

    def link_to_thread(self):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('core:thread', kwargs={'thread_id': self.thread.pk}),
            self.thread.name
        )

    link_to_thread.short_description = 'Link to thread'

    def __str__(self):
        return '{}: {}'.format(self.thread_id, get_username_by_uid(self))


class Message(models.Model):
    thread = models.ForeignKey(
        Thread,
        related_name='messages',
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    lang = models.CharField(
        max_length=2,
        choices=settings.LANGUAGES,
        default='en'
    )
    date = models.DateTimeField(auto_now_add=True)

    def link_to_thread(self):
        return format_html(
            '<a href="{}">{}</a>',
            reverse('core:thread', kwargs={'thread_id': self.thread.pk}),
            self.thread.name
        )

    link_to_thread.short_description = 'Link to thread'

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.thread.last_message = datetime.datetime.now()
        self.thread.save()
        super(Message, self).save(force_insert=False, force_update=False,
                                  using=None, update_fields=None)

    def __str__(self):
        return '{}: {}'.format(get_username_by_uid(self), self.text[:100])


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
