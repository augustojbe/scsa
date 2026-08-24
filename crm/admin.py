from django.contrib import admin

from base.admin import TenantAdminMixin
from crm.models import Deal, Pipeline, PipelineStage


@admin.register(Pipeline)
class PipelineAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'is_default']
    search_fields = ['name']
    list_filter = ['is_default']


@admin.register(PipelineStage)
class PipelineStageAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'pipeline', 'color', 'order']
    search_fields = ['name', 'pipeline__name']


@admin.register(Deal)
class DealAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['title', 'client', 'pipeline', 'stage', 'value']
    search_fields = ['title', 'client__name']
    list_filter = ['pipeline', 'stage']
