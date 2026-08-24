from django import forms

from agents.models import Agent, Producer


class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ['name', 'document', 'type', 'commission_rate']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'document': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'commission_rate': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}
            ),
        }


class ProducerForm(forms.ModelForm):
    class Meta:
        model = Producer
        fields = ['agent', 'name', 'document', 'commission_rate']
        widgets = {
            'agent': forms.Select(attrs={'class': 'form-select'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'document': forms.TextInput(attrs={'class': 'form-control'}),
            'commission_rate': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0', 'max': '100'}
            ),
        }

    def __init__(self, *args, brokerage=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.brokerage = brokerage
        if brokerage is not None:
            self.fields['agent'].queryset = Agent.all_objects.filter(brokerage=brokerage)
        else:
            self.fields['agent'].queryset = self.fields['agent'].queryset.none()
