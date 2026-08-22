from django.db import models

from base.tenant import get_current_brokerage


class TenantManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        brokerage = get_current_brokerage()
        if brokerage is not None:
            queryset = queryset.filter(brokerage=brokerage)
        return queryset
