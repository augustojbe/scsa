from django.contrib import admin

from base.admin import TenantAdminMixin
from insurers.models import Branch, Insurer


@admin.register(Insurer)
class InsurerAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'code', 'is_active']
    search_fields = ['name', 'code']
    list_filter = ['is_active']


@admin.register(Branch)
class BranchAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']
