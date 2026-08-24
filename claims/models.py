from django.db import models
from django.utils import timezone

from base.constants import (
    CLAIM_OPEN,
    CLAIM_STATUS_CHOICES,
    CLAIM_TYPE_CHOICES,
    CLAIM_TYPE_OTHER,
)
from base.models import BaseTenantModel


class Claim(BaseTenantModel):
    policy = models.ForeignKey(
        'policies.Policy',
        on_delete=models.PROTECT,
        related_name='claims',
    )
    covered_item = models.ForeignKey(
        'policies.CoveredItem',
        on_delete=models.PROTECT,
        related_name='claims',
    )
    number = models.CharField(max_length=30, unique=True, blank=True)
    type = models.CharField(
        max_length=20,
        choices=CLAIM_TYPE_CHOICES,
        default=CLAIM_TYPE_OTHER,
    )
    status = models.CharField(
        max_length=20,
        choices=CLAIM_STATUS_CHOICES,
        default=CLAIM_OPEN,
    )
    reported_at = models.DateTimeField(default=timezone.now)
    description = models.TextField(blank=True)
    reserved_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    ai_summary = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Sinistro {self.number} — {self.policy.client}'

    @property
    def client(self):
        return self.policy.client

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.number:
            year = timezone.localdate().year
            self.number = f'SIN-{year}-{self.pk:06d}'
            super().save(update_fields=['number'])


class ClaimAttachment(BaseTenantModel):
    claim = models.ForeignKey(
        'claims.Claim',
        on_delete=models.CASCADE,
        related_name='attachments',
    )
    file = models.FileField(upload_to='claims/attachments/')
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.description or self.file.name

    @property
    def filename(self):
        return self.file.name.split('/')[-1]
