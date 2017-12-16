from django.contrib import admin

from .models import Profile, Thread, UnreadThread, Message


class ProfileAdmin(admin.ModelAdmin):
    readonly_fields = ('preview', 'location')
    search_fields = ['user__username']


class ThreadAdmin(admin.ModelAdmin):
    readonly_fields = ('last_message', 'link_to_thread',)
    search_fields = ['users__username']


class UnreadThreadAdmin(admin.ModelAdmin):
    readonly_fields = ('date', 'link_to_thread',)
    search_fields = ['user__username']


class MessageAdmin(admin.ModelAdmin):
    readonly_fields = ('date', 'link_to_thread',)
    search_fields = ['user__username', 'text']


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Thread, ThreadAdmin)
admin.site.register(UnreadThread, UnreadThreadAdmin)
admin.site.register(Message, MessageAdmin)
