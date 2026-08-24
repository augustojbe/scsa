from django.db import models

from base.models import BaseTenantModel


class Pipeline(BaseTenantModel):
    name = models.CharField(max_length=255)
    is_default = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class PipelineStage(BaseTenantModel):
    pipeline = models.ForeignKey(
        'crm.Pipeline',
        on_delete=models.CASCADE,
        related_name='stages',
    )
    name = models.CharField(max_length=255)
    color = models.CharField(max_length=7, default='#0d6efd')
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return f'{self.name} ({self.pipeline.name})'


class Deal(BaseTenantModel):
    pipeline = models.ForeignKey(
        'crm.Pipeline',
        on_delete=models.PROTECT,
        related_name='deals',
    )
    stage = models.ForeignKey(
        'crm.PipelineStage',
        on_delete=models.PROTECT,
        related_name='deals',
    )
    client = models.ForeignKey(
        'clients.Client',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='deals',
    )
    proposal = models.ForeignKey(
        'policies.Proposal',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='deals',
    )
    title = models.CharField(max_length=255)
    value = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    expected_close_date = models.DateField(null=True, blank=True)
    order = models.PositiveIntegerField(default=0)
    ai_summary = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.title
