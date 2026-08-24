from django.contrib import admin

from agents.models import Agent, Producer


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display = ['name', 'document', 'type', 'commission_rate', 'brokerage']
    search_fields = ['name', 'document']
    list_filter = ['type', 'brokerage']


@admin.register(Producer)
class ProducerAdmin(admin.ModelAdmin):
    list_display = ['name', 'agent', 'document', 'commission_rate', 'brokerage']
    search_fields = ['name', 'document']
    list_filter = ['brokerage']
