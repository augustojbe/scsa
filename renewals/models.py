from django.db import models

from base.constants import RENEWAL_PENDING, RENEWAL_STATUS_CHOICES
from base.models import BaseTenantModel


class Renewal(BaseTenantModel):
    policy = models.ForeignKey(
        'policies.Policy',
        on_delete=models.PROTECT,
        related_name='renewals',
    )
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,
        related_name='renewals',
    )
    due_date = models.DateField()
    status = models.CharField(
        max_length=20,
        choices=RENEWAL_STATUS_CHOICES,
        default=RENEWAL_PENDING,
    )
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f'Renovação {self.policy.number} — {self.client.name}'

    def is_overdue(self):
        from django.utils import timezone
        return self.due_date < timezone.localdate() and self.status == RENEWAL_PENDING
