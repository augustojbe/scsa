from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.models import Brokerage, User


@admin.register(Brokerage)
class BrokerageAdmin(admin.ModelAdmin):
    list_display = ['cnpj', 'legal_name', 'trade_name', 'plan', 'is_active']
    search_fields = ['cnpj', 'legal_name', 'trade_name']
    list_filter = ['plan', 'is_active']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ['email']
    list_display = ['email', 'full_name', 'brokerage', 'role', 'is_staff', 'is_active']
    search_fields = ['email', 'full_name']
    list_filter = ['role', 'is_staff', 'is_active', 'brokerage']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('full_name', 'brokerage', 'role')}),
        (
            'Permissions',
            {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')},
        ),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (
            None,
            {
                'classes': ('wide',),
                'fields': ('email', 'full_name', 'password1', 'password2'),
            },
        ),
    )
