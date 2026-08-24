from django import forms

from clients.models import Client
from policies.models import Policy

from renewals.models import Renewal


class RenewalForm(forms.ModelForm):
    class Meta:
        model = Renewal
        fields = ['policy', 'due_date', 'status', 'notes']
        widgets = {
            'policy': forms.Select(attrs={'class': 'form-select'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, brokerage=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.brokerage = brokerage
        if brokerage is not None:
            self.fields['policy'].queryset = Policy.all_objects.filter(brokerage=brokerage)
        else:
            self.fields['policy'].queryset = self.fields['policy'].queryset.none()

    def clean(self):
        cleaned_data = super().clean()
        policy = cleaned_data.get('policy')
        client = None
        if policy is not None:
            client = policy.client
        cleaned_data['client'] = client
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.client = self.cleaned_data.get('client')
        if commit:
            instance.save()
        return instance
