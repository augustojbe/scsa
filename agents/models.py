from django.db import models

from base.constants import AGENT_COMPANY, AGENT_TYPE_CHOICES
from base.models import BaseTenantModel


class Agent(BaseTenantModel):
    name = models.CharField(max_length=255)
    document = models.CharField(max_length=14, blank=True)
    type = models.CharField(
        max_length=20,
        choices=AGENT_TYPE_CHOICES,
        default=AGENT_COMPANY,
    )
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text='Percentual de repasse pago ao agente (0 a 100).',
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Producer(BaseTenantModel):
    agent = models.ForeignKey(
        'agents.Agent',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='producers',
    )
    name = models.CharField(max_length=255)
    document = models.CharField(max_length=14, blank=True)
    commission_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0,
        help_text='Percentual de repasse pago ao produtor (0 a 100).',
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
