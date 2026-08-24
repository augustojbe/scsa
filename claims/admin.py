from django.contrib import admin

from base.admin import TenantAdminMixin
from claims.models import Claim, ClaimAttachment


@admin.register(Claim)
class ClaimAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['number', 'policy', 'covered_item', 'type', 'status', 'reported_at']
    search_fields = ['number', 'policy__client__name']
    list_filter = ['type', 'status']


@admin.register(ClaimAttachment)
class ClaimAttachmentAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['claim', 'description', 'created_at']
    search_fields = ['claim__number', 'description']
