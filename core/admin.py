from django.contrib import admin

from .models import LoggedInUser, Thread, Message

admin.site.register(LoggedInUser)
admin.site.register(Thread)
admin.site.register(Message)
