from django.contrib import admin

from renewals.models import Renewal


@admin.register(Renewal)
class RenewalAdmin(admin.ModelAdmin):
    list_display = ['policy', 'client', 'due_date', 'status', 'brokerage']
    search_fields = ['policy__number', 'client__name']
    list_filter = ['status', 'due_date', 'brokerage']
