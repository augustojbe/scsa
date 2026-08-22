from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from base.constants import PLAN_CHOICES, PLAN_FREE, ROLE_CHOICES, ROLE_OWNER
from base.models import BaseModel


class Brokerage(BaseModel):
    cnpj = models.CharField(max_length=14, unique=True)
    legal_name = models.CharField(max_length=255)
    trade_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    street = models.CharField(max_length=255, blank=True)
    number = models.CharField(max_length=20, blank=True)
    complement = models.CharField(max_length=100, blank=True)
    neighborhood = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=2, blank=True)
    zip_code = models.CharField(max_length=9, blank=True)
    logo = models.ImageField(upload_to='brokerages/logos/', null=True, blank=True)
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, default=PLAN_FREE)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'brokerage'
        verbose_name_plural = 'brokerages'

    def __str__(self):
        return self.trade_name or self.legal_name


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, full_name, password, **extra_fields):
        if not email:
            raise ValueError('The email must be set.')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, full_name, password, **extra_fields)

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(email, full_name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    brokerage = models.ForeignKey(
        'core.Brokerage',
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name='users',
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_OWNER)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __str__(self):
        return self.email

    def clean(self):
        if not self.is_superuser and self.brokerage is None:
            raise ValidationError(
                {'brokerage': 'Brokerage is required for non-superusers.'}
            )

    def save(self, *args, **kwargs):
        if not self.is_superuser and self.brokerage_id is None:
            raise ValidationError(
                {'brokerage': 'Brokerage is required for non-superusers.'}
            )
        super().save(*args, **kwargs)

    @property
    def initials(self):
        parts = self.full_name.strip().split()
        if not parts:
            return 'U'
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()
