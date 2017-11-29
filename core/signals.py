from django.contrib.auth import user_logged_in, user_logged_out
from django.contrib.gis.geoip2 import GeoIP2
from django.core.cache import cache
from django.dispatch import receiver

from .models import Profile


@receiver(user_logged_in)
def on_user_loggedin(sender, user, request, **kwargs):
    if user.is_authenticated():
        # If there no user profile - create it.
        profile, _ = Profile.objects.get_or_create(user=user)

        # Update user coordinates.
        ip = request.META.get('REMOTE_ADDR')
        if ip and ip != '127.0.0.1' and not all([profile.lon, profile.lat]):
            g = GeoIP2()
            profile.lon, profile.lat = g.lon_lat(ip)
            profile.save()


@receiver(user_logged_out)
def on_user_logout(sender, **kwargs):
    user = kwargs.get('user')
    if user.is_authenticated():
        cache.delete('seen_{}'.format(user.username))
