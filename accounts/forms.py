from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from base.constants import PLAN_FREE
from base.utils import only_digits
from core.models import User


class SignupForm(forms.Form):
    cnpj = forms.CharField(
        max_length=18,
        label='CNPJ',
        widget=forms.TextInput(attrs={'placeholder': '00.000.000/0000-00'}),
    )
    legal_name = forms.CharField(max_length=255, label='Razão Social')
    trade_name = forms.CharField(
        max_length=255,
        label='Nome Fantasia',
        required=False,
    )
    brokerage_email = forms.EmailField(label='E-mail da corretora', required=False)
    phone = forms.CharField(max_length=30, label='Telefone', required=False)
    full_name = forms.CharField(max_length=255, label='Nome completo')
    email = forms.EmailField(label='E-mail')
    password = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )
    password_confirm = forms.CharField(
        label='Confirmar senha',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
    )

    def clean_cnpj(self):
        cnpj = only_digits(self.cleaned_data.get('cnpj'))
        if len(cnpj) != 14:
            raise ValidationError('Informe um CNPJ válido com 14 dígitos.')
        return cnpj

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Já existe uma conta com este e-mail.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'As senhas não coincidem.')
        if password:
            try:
                validate_password(password)
            except ValidationError as error:
                self.add_error('password', error.messages[0])
        return cleaned_data

    def save(self):
        from core.models import Brokerage

        brokerage = Brokerage(
            cnpj=self.cleaned_data['cnpj'],
            legal_name=self.cleaned_data['legal_name'],
            trade_name=self.cleaned_data.get('trade_name', ''),
            email=self.cleaned_data.get('brokerage_email', ''),
            phone=self.cleaned_data.get('phone', ''),
            plan=PLAN_FREE,
        )
        brokerage.save()
        user = User(
            email=self.cleaned_data['email'],
            full_name=self.cleaned_data['full_name'],
            brokerage=brokerage,
        )
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user
