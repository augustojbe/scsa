from django.contrib import admin

from base.admin import TenantAdminMixin
from clients.models import Client, ClientAttachment


@admin.register(Client)
class ClientAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'document', 'type', 'email', 'phone', 'city']
    search_fields = ['name', 'document', 'email']
    list_filter = ['type']


@admin.register(ClientAttachment)
class ClientAttachmentAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['client', 'description', 'created_at']
    search_fields = ['client__name', 'description']
