from django.db import models

from base.models import BaseTenantModel


class Insurer(BaseTenantModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Branch(BaseTenantModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        verbose_name_plural = 'branches'

    def __str__(self):
        return self.name
