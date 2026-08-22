from django.db import models

from base.constants import CLIENT_TYPE_CHOICES, CLIENT_TYPE_PERSON
from base.models import BaseTenantModel


class Client(BaseTenantModel):
    name = models.CharField(max_length=255)
    document = models.CharField(max_length=14, blank=True)
    type = models.CharField(
        max_length=2,
        choices=CLIENT_TYPE_CHOICES,
        default=CLIENT_TYPE_PERSON,
    )
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    street = models.CharField(max_length=255, blank=True)
    number = models.CharField(max_length=20, blank=True)
    complement = models.CharField(max_length=100, blank=True)
    neighborhood = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip_code = models.CharField(max_length=9, blank=True)
    ai_summary = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class ClientAttachment(BaseTenantModel):
    client = models.ForeignKey(
        'clients.Client',
        on_delete=models.CASCADE,
        related_name='attachments',
    )
    file = models.FileField(upload_to='clients/attachments/')
    description = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.description or self.file.name

    @property
    def filename(self):
        return self.file.name.split('/')[-1]
