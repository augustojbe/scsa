from django.db import models

from base.constants import COMMISSION_PENDING, COMMISSION_STATUS_CHOICES
from base.models import BaseTenantModel


class Commission(BaseTenantModel):
    policy = models.ForeignKey(
        'policies.Policy',
        on_delete=models.PROTECT,
        related_name='commissions',
    )
    insurer = models.ForeignKey(
        'insurers.Insurer',
        on_delete=models.PROTECT,
        related_name='commissions',
    )
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,
        related_name='commissions',
    )
    agent = models.ForeignKey(
        'agents.Agent',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='commissions',
    )
    producer = models.ForeignKey(
        'agents.Producer',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='commissions',
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    agent_share = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    producer_share = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    brokerage_share = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    computed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=COMMISSION_STATUS_CHOICES,
        default=COMMISSION_PENDING,
    )

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comissão {self.policy.number} — R$ {self.total_amount}'

    def compute_shares(self):
        total = float(self.total_amount or 0)
        agent_rate = float(self.agent.commission_rate if self.agent else 0)
        producer_rate = float(self.producer.commission_rate if self.producer else 0)
        agent_share = total * agent_rate / 100.0
        producer_share = total * producer_rate / 100.0
        brokerage_share = total - agent_share - producer_share
        self.agent_share = round(agent_share, 2)
        self.producer_share = round(producer_share, 2)
        self.brokerage_share = round(brokerage_share, 2)
        return self
