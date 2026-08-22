from django.contrib.auth.mixins import AccessMixin, LoginRequiredMixin

from base.constants import MANAGEMENT_ROLES


class RoleRequiredMixin(AccessMixin):
    allowed_roles = []

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if (
            self.allowed_roles
            and request.user.role not in self.allowed_roles
            and not request.user.is_superuser
        ):
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class ManagementRequiredMixin(RoleRequiredMixin):
    allowed_roles = MANAGEMENT_ROLES


class BrokerageRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.brokerage:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
