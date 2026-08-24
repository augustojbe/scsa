from django.contrib import admin

from commissions.models import Commission


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = [
        'policy', 'client', 'insurer', 'total_amount', 'agent_share',
        'producer_share', 'brokerage_share', 'status', 'brokerage',
    ]
    search_fields = ['policy__number', 'client__name']
    list_filter = ['status', 'insurer', 'brokerage']
