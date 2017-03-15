from django.contrib import admin

from .models import Profile, Thread, UnreadThread, Message

admin.site.register(Profile)
admin.site.register(Thread)
admin.site.register(UnreadThread)
admin.site.register(Message)
