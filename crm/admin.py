from django.contrib import admin

from crm.models import Deal, Pipeline, PipelineStage


@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_default', 'brokerage']
    search_fields = ['name']
    list_filter = ['is_default', 'brokerage']


@admin.register(PipelineStage)
class PipelineStageAdmin(admin.ModelAdmin):
    list_display = ['name', 'pipeline', 'color', 'order', 'brokerage']
    search_fields = ['name', 'pipeline__name']
    list_filter = ['brokerage']


@admin.register(Deal)
class DealAdmin(admin.ModelAdmin):
    list_display = ['title', 'client', 'pipeline', 'stage', 'value', 'brokerage']
    search_fields = ['title', 'client__name']
    list_filter = ['pipeline', 'stage', 'brokerage']
