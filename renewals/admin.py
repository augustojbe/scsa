from django.contrib import admin

from base.admin import TenantAdminMixin
from renewals.models import Renewal


@admin.register(Renewal)
class RenewalAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['policy', 'client', 'due_date', 'status']
    search_fields = ['policy__number', 'client__name']
    list_filter = ['status', 'due_date']
