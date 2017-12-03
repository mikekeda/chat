from django.conf import settings
from django.urls import path

from .views import (log_in, log_out, sign_up, user_list, thread_view,
                    call_view, ProfileView)


app_name = "Chat"

urlpatterns = [
    path('login', log_in, name='login'),
    path('logout', log_out, name='logout'),
    path('signup', sign_up, name='signup'),
    path('', user_list, name='user_list'),
    path('user/<str:username>', ProfileView.as_view(), name='user'),
    path('chat/<str:username>', thread_view, name='chat'),
    path('thread/<int:thread_id>', thread_view, name='thread'),
    path('call/<str:username>', call_view, name='call'),
]

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
