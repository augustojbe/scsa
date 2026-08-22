from django.db import models

from base.managers import TenantManager


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BaseTenantModel(BaseModel):
    brokerage = models.ForeignKey(
        'core.Brokerage',
        on_delete=models.PROTECT,
        related_name='%(class)ss',
    )

    objects = TenantManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
