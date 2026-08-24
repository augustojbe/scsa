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


class Notification(BaseTenantModel):
    user = models.ForeignKey(
        'core.User',
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    message = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.message
