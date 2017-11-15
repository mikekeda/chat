from django.contrib import admin

from .models import Profile, Thread, UnreadThread, Message


class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('preview',)


class ThreadAdmin(admin.ModelAdmin):
    readonly_fields = ('last_message', 'link_to_thread',)


class UnreadThreadAdmin(admin.ModelAdmin):
    readonly_fields = ('date', 'link_to_thread',)


class MessageAdmin(admin.ModelAdmin):
    readonly_fields = ('date', 'link_to_thread',)


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(UnreadThread, UnreadThreadAdmin)
admin.site.register(Message, MessageAdmin)
