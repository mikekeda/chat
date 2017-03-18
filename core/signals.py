from django.contrib.auth import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.core.cache import cache

from .models import Profile


@receiver(user_logged_in)
def on_user_loggedin(sender, **kwargs):
    user = kwargs.get('user')
    if user.is_authenticated():
        # If there no user profile - create it.
        Profile.objects.get_or_create(user=user)


@receiver(user_logged_out)
def on_user_logout(sender, **kwargs):
    user = kwargs.get('user')
    if user.is_authenticated():
        cache.delete('seen_%s' % user.username)
