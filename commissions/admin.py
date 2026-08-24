from django.contrib import admin

from base.admin import TenantAdminMixin
from commissions.models import Commission


@admin.register(Commission)
class CommissionAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = [
        'policy', 'client', 'insurer', 'total_amount', 'agent_share',
        'producer_share', 'brokerage_share', 'status',
    ]
    search_fields = ['policy__number', 'client__name']
    list_filter = ['status', 'insurer']
