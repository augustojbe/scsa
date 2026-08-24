from django.contrib import admin
from django.core.exceptions import ValidationError

from base.models import Notification


class TenantAdminMixin:
    """Filtra objetos por brokerage do usuário (exceto superuser) e valida no save."""

    tenant_field = 'brokerage'

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        if request.user.is_superuser:
            return queryset
        if not getattr(request.user, 'brokerage', None):
            return queryset.none()
        return queryset.filter(**{self.tenant_field: request.user.brokerage})

    def get_form_queryset_for_field(self, request, field_name, default_queryset):
        if request.user.is_superuser:
            return default_queryset
        brokerage = getattr(request.user, 'brokerage', None)
        if brokerage is None:
            return default_queryset.none()
        if hasattr(default_queryset.model, self.tenant_field):
            return default_queryset.filter(**{self.tenant_field: brokerage})
        return default_queryset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)
        field.queryset = self.get_form_queryset_for_field(
            request, db_field.name, field.queryset
        )
        return field

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        field = super().formfield_for_manytomany(db_field, request, **kwargs)
        field.queryset = self.get_form_queryset_for_field(
            request, db_field.name, field.queryset
        )
        return field

    def save_model(self, request, obj, form, change):
        if not request.user.is_superuser:
            brokerage = getattr(request.user, 'brokerage', None)
            if brokerage is None:
                raise ValidationError('Usuário não vinculado a uma corretora.')
            setattr(obj, self.tenant_field, brokerage)
        super().save_model(request, obj, form, change)

    def get_list_display(self, request):
        display = list(super().get_list_display(request))
        if self.tenant_field not in display and hasattr(self.model, self.tenant_field):
            display.append(self.tenant_field)
        return display


@admin.register(Notification)
class NotificationAdmin(TenantAdminMixin, admin.ModelAdmin):
    list_display = ['user', 'message', 'is_read', 'created_at']
    search_fields = ['message', 'user__email']
    list_filter = ['is_read']
