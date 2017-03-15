from django.contrib.auth import user_logged_out
from django.dispatch import receiver
from django.core.cache import cache


@receiver(user_logged_out)
def on_user_logout(sender, **kwargs):
    user = kwargs.get('user')
    if user.is_authenticated():
        cache.delete('seen_%s' % user.username)
