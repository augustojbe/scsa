from django.contrib import admin

from base.admin import TenantAdminMixin
from policies.models import (
    Coverage,
    CoveredItem,
    Endorsement,
    Policy,
    PolicyAttachment,
    Proposal,
    ProposalAttachment,
)


@admin.register(Endorsement)
class EndorsementAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['number', 'policy', 'type', 'effective_date']
    search_fields = ['number', 'policy__number']
    list_filter = ['type']


@admin.register(Policy)
class PolicyAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['number', 'client', 'insurer', 'branch', 'status', 'premium', 'start_date', 'end_date']
    search_fields = ['number', 'client__name']
    list_filter = ['status', 'branch', 'insurer']


@admin.register(PolicyAttachment)
class PolicyAttachmentAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['policy', 'description', 'created_at']
    search_fields = ['policy__number', 'description']


@admin.register(Proposal)
class ProposalAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['pk', 'client', 'insurer', 'branch', 'status', 'premium']
    search_fields = ['client__name']
    list_filter = ['status', 'branch', 'insurer']


@admin.register(ProposalAttachment)
class ProposalAttachmentAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['proposal', 'description', 'created_at']
    search_fields = ['proposal__client__name', 'description']


@admin.register(Coverage)
class CoverageAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'branch']
    search_fields = ['name']
    list_filter = ['branch']


@admin.register(CoveredItem)
class CoveredItemAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['description', 'type']
    search_fields = ['description']
    list_filter = ['type']
