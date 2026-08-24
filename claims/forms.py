from django import forms
from django.core.exceptions import ValidationError

from policies.models import CoveredItem, Policy

from claims.models import Claim, ClaimAttachment


class ClaimAttachmentForm(forms.ModelForm):
    class Meta:
        model = ClaimAttachment
        fields = ['file', 'description']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Descrição (opcional)'}
            ),
        }


class ClaimForm(forms.ModelForm):
    class Meta:
        model = Claim
        fields = [
            'policy',
            'covered_item',
            'type',
            'status',
            'reported_at',
            'reserved_amount',
            'description',
        ]
        widgets = {
            'policy': forms.Select(attrs={'class': 'form-select'}),
            'covered_item': forms.Select(attrs={'class': 'form-select'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'reported_at': forms.DateTimeInput(
                attrs={'class': 'form-control', 'type': 'datetime-local'}
            ),
            'reserved_amount': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}
            ),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, brokerage=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.brokerage = brokerage
        if brokerage is not None:
            self.fields['policy'].queryset = Policy.all_objects.filter(brokerage=brokerage)
            self.fields['covered_item'].queryset = (
                CoveredItem.all_objects.filter(brokerage=brokerage)
            )
        else:
            self.fields['policy'].queryset = self.fields['policy'].queryset.none()
            self.fields['covered_item'].queryset = (
                self.fields['covered_item'].queryset.none()
            )

    def clean(self):
        cleaned_data = super().clean()
        policy = cleaned_data.get('policy')
        covered_item = cleaned_data.get('covered_item')
        if policy and covered_item:
            if policy.brokerage_id != covered_item.brokerage_id:
                raise ValidationError('Selecione registros da mesma corretora.')
            if not policy.covered_items.filter(pk=covered_item.pk).exists():
                raise ValidationError(
                    'O item coberto deve estar associado à apólice selecionada.'
                )
        return cleaned_data
