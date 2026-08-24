from django.contrib import admin

from agents.models import Agent, Producer
from base.admin import TenantAdminMixin


@admin.register(Agent)
class AgentAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'document', 'type', 'commission_rate']
    search_fields = ['name', 'document']
    list_filter = ['type']


@admin.register(Producer)
class ProducerAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'agent', 'document', 'commission_rate']
    search_fields = ['name', 'document']
