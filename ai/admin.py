from django.contrib import admin

from ai.models import ChatMessage, ChatSession
from base.admin import TenantAdminMixin


@admin.register(ChatSession)
class ChatSessionAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['title', 'user', 'created_at']
    search_fields = ['title', 'user__email']
    list_filter = ['user']


@admin.register(ChatMessage)
class ChatMessageAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['session', 'role', 'created_at']
    search_fields = ['session__title', 'content']
    list_filter = ['role']
