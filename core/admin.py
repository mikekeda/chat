from django.contrib import admin

from .models import Profile, Thread, Message

admin.site.register(Profile)
admin.site.register(Thread)
admin.site.register(Message)
