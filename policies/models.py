from django.db import models
from django.utils import timezone

from base.constants import (
    COVERED_ITEM_OTHER,
    COVERED_ITEM_TYPE_CHOICES,
    ENDORSEMENT_OTHER,
    ENDORSEMENT_TYPE_CHOICES,
    POLICY_ACTIVE,
    POLICY_STATUS_CHOICES,
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


class Policy(BaseTenantModel):
    number = models.CharField(max_length=30, unique=True, blank=True)
    proposal = models.ForeignKey(
        'policies.Proposal',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='policies',
    )
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.PROTECT,
        related_name='policies',
    )
    insurer = models.ForeignKey(
        'insurers.Insurer',
        on_delete=models.PROTECT,
        related_name='policies',
    )
    branch = models.ForeignKey(
        'insurers.Branch',
        on_delete=models.PROTECT,
        related_name='policies',
    )
    number_prefix = 'AP'
    status = models.CharField(
        max_length=20,
        choices=POLICY_STATUS_CHOICES,
        default=POLICY_ACTIVE,
    )
    premium = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    coverages = models.ManyToManyField('policies.Coverage', blank=True, related_name='policies')
    covered_items = models.ManyToManyField('policies.CoveredItem', blank=True, related_name='policies')
    ai_summary = models.TextField(null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Apólice {self.number} — {self.client}'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.number:
            self.number = f'{self.number_prefix}-{timezone.localdate().year}-{self.pk:06d}'
            super().save(update_fields=['number'])


class PolicyAttachment(BaseTenantModel):
    policy = models.ForeignKey(
        'policies.Policy',
        on_delete=models.CASCADE,
        related_name='attachments',
    )
    file = models.FileField(upload_to='policies/attachments/')
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.description or self.file.name

    @property
    def filename(self):
        return self.file.name.split('/')[-1]


class Endorsement(BaseTenantModel):
    policy = models.ForeignKey(
        'policies.Policy',
        on_delete=models.CASCADE,
        related_name='endorsements',
    )
    number = models.CharField(max_length=30, blank=True)
    type = models.CharField(
        max_length=20,
        choices=ENDORSEMENT_TYPE_CHOICES,
        default=ENDORSEMENT_OTHER,
    )
    description = models.TextField(blank=True)
    effective_date = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ['-effective_date', '-created_at']

    def __str__(self):
        return f'Endosso {self.number} — {self.policy.number}'

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        if not self.number:
            self.number = f'{self.policy.number}-E'
        super().save(*args, **kwargs)
        if is_new and self.number.endswith('-E'):
            self.number = f'{self.policy.number}-E{self.pk}'
            super().save(update_fields=['number'])
