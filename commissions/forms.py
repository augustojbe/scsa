from django import forms
from django.utils import timezone

from agents.models import Agent, Producer
from policies.models import Policy

from commissions.models import Commission


class CommissionForm(forms.ModelForm):
    class Meta:
        model = Commission
        fields = ['policy', 'agent', 'producer', 'total_amount', 'status']
        widgets = {
            'policy': forms.Select(attrs={'class': 'form-select'}),
            'agent': forms.Select(attrs={'class': 'form-select'}),
            'producer': forms.Select(attrs={'class': 'form-select'}),
            'total_amount': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}
            ),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, brokerage=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.brokerage = brokerage
        if brokerage is not None:
            self.fields['policy'].queryset = Policy.all_objects.filter(brokerage=brokerage)
            self.fields['agent'].queryset = Agent.all_objects.filter(brokerage=brokerage)
            self.fields['producer'].queryset = Producer.all_objects.filter(
                brokerage=brokerage
            )
        else:
            for name in ('policy', 'agent', 'producer'):
                self.fields[name].queryset = self.fields[name].queryset.none()

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.insurer = instance.policy.insurer
        instance.client = instance.policy.client
        instance.compute_shares()
        instance.computed_at = timezone.now()
        if commit:
            instance.save()
        return instance
