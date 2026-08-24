from django.contrib import admin

from ai.models import ChatMessage, ChatSession


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'brokerage', 'created_at']
    search_fields = ['title', 'user__email']
    list_filter = ['brokerage']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['session', 'role', 'created_at']
    search_fields = ['session__title', 'content']
    list_filter = ['role', 'brokerage']
