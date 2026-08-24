from django.contrib import admin

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
class EndorsementAdmin(admin.ModelAdmin):
    list_display = ['number', 'policy', 'type', 'effective_date', 'brokerage']
    search_fields = ['number', 'policy__number']
    list_filter = ['type', 'brokerage']


@admin.register(Policy)
class PolicyAdmin(admin.ModelAdmin):
    list_display = ['number', 'client', 'insurer', 'branch', 'status', 'premium', 'start_date', 'end_date']
    search_fields = ['number', 'client__name']
    list_filter = ['status', 'branch', 'insurer', 'brokerage']


@admin.register(PolicyAttachment)
class PolicyAttachmentAdmin(admin.ModelAdmin):
    list_display = ['policy', 'description', 'created_at']
    search_fields = ['policy__number', 'description']
    list_filter = ['brokerage']


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ['pk', 'client', 'insurer', 'branch', 'status', 'premium']
    search_fields = ['client__name']
    list_filter = ['status', 'branch', 'insurer', 'brokerage']


@admin.register(ProposalAttachment)
class ProposalAttachmentAdmin(admin.ModelAdmin):
    list_display = ['proposal', 'description', 'created_at']
    search_fields = ['proposal__client__name', 'description']
    list_filter = ['brokerage']


@admin.register(Coverage)
class CoverageAdmin(admin.ModelAdmin):
    list_display = ['name', 'branch', 'brokerage']
    search_fields = ['name']
    list_filter = ['branch', 'brokerage']


@admin.register(CoveredItem)
class CoveredItemAdmin(admin.ModelAdmin):
    list_display = ['description', 'type', 'brokerage']
    search_fields = ['description']
    list_filter = ['type', 'brokerage']
