from django.conf.urls import url
from .views import log_in, log_out, sign_up, user_list, thread


urlpatterns = [
    url(r'^login$', log_in, name='login'),
    url(r'^logout$', log_out, name='logout'),
    url(r'^signup$', sign_up, name='signup'),
    url(r'^$', user_list, name='user_list'),
    url(r'^chat/(?P<username>.+)$', thread, name='user'),
    url(r'^thread/(?P<thread_id>.+)$', thread, name='thread'),
]