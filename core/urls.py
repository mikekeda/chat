from django.conf.urls import url
from django.conf import settings

from .views import log_in, log_out, sign_up, user_list, thread_view, call_view, profile_view, update_profile


urlpatterns = [
    url(r'^login$', log_in, name='login'),
    url(r'^logout$', log_out, name='logout'),
    url(r'^signup$', sign_up, name='signup'),
    url(r'^$', user_list, name='user_list'),
    url(r'^user/(?P<username>.+)$', profile_view, name='user'),
    url(r'^chat/(?P<username>.+)$', thread_view, name='chat'),
    url(r'^thread/(?P<thread_id>.+)$', thread_view, name='thread'),
    url(r'^call/(?P<username>.+)$', call_view, name='call'),
    url(r'^update-profile$', update_profile, name='update_profile'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
