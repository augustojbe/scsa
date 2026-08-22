from django.db import models

from base.constants import (
    COVERED_ITEM_OTHER,
    COVERED_ITEM_TYPE_CHOICES,
    PROPOSAL_DRAFT,
    PROPOSAL_STATUS_CHOICES,
)
from base.models import BaseTenantModel


class Coverage(BaseTenantModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    branch = models.ForeignKey(
        'insurers.Branch',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='coverages',
    )

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class CoveredItem(BaseTenantModel):
    type = models.CharField(
        max_length=20,
        choices=COVERED_ITEM_TYPE_CHOICES,
        default=COVERED_ITEM_OTHER,
    )
    description = models.CharField(max_length=255)
    attributes = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['description']

    def __str__(self):
        return self.description


class Proposal(BaseTenantModel):
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,
        related_name='proposals',
    )
    insurer = models.ForeignKey(
        'insurers.Insurer',
        on_delete=models.PROTECT,
        related_name='proposals',
    )
    branch = models.ForeignKey(
        'insurers.Branch',
        on_delete=models.PROTECT,
        related_name='proposals',
    )
    status = models.CharField(
        max_length=20,
        choices=PROPOSAL_STATUS_CHOICES,
        default=PROPOSAL_DRAFT,
    )
    premium = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    coverages = models.ManyToManyField('policies.Coverage', blank=True, related_name='proposals')
    covered_items = models.ManyToManyField('policies.CoveredItem', blank=True, related_name='proposals')
    ai_summary = models.TextField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Proposta #{self.pk} — {self.client}'


class ProposalAttachment(BaseTenantModel):
    proposal = models.ForeignKey(
        'policies.Proposal',
        on_delete=models.CASCADE,
        related_name='attachments',
    )
    file = models.FileField(upload_to='policies/proposals/attachments/')
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.description or self.file.name

    @property
    def filename(self):
        return self.file.name.split('/')[-1]
