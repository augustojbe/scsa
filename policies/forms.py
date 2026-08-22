from django import forms

from insurers.models import Branch
from policies.models import Coverage, CoveredItem, Proposal, ProposalAttachment


class ProposalAttachmentForm(forms.ModelForm):
    class Meta:
        model = ProposalAttachment
        fields = ['file', 'description']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Descrição (opcional)'}
            ),
        }


class CoverageForm(forms.ModelForm):
    class Meta:
        model = Coverage
        fields = ['name', 'description', 'branch']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, brokerage=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.brokerage = brokerage
        if brokerage is not None:
            self.fields['branch'].queryset = Branch.all_objects.filter(brokerage=brokerage)
        else:
            self.fields['branch'].queryset = Branch.objects.none()


class CoveredItemForm(forms.ModelForm):
    class Meta:
        model = CoveredItem
        fields = ['type', 'description', 'attributes']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'attributes': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': '{"placa": "ABC1D23", "ano": 2023}',
                }
            ),
        }

    def clean_attributes(self):
        attributes = self.cleaned_data.get('attributes')
        if isinstance(attributes, str):
            try:
                import json

                attributes = json.loads(attributes)
            except ValueError:
                raise forms.ValidationError('Informe um JSON válido.')
        return attributes or {}


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = [
            'client',
            'insurer',
            'branch',
            'status',
            'premium',
            'coverages',
            'covered_items',
            'notes',
        ]
        widgets = {
            'client': forms.Select(attrs={'class': 'form-select'}),
            'insurer': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'premium': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}
            ),
            'coverages': forms.CheckboxSelectMultiple(),
            'covered_items': forms.CheckboxSelectMultiple(),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, brokerage=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.brokerage = brokerage
        if brokerage is not None:
            self.fields['client'].queryset = (
                self.fields['client'].queryset.model.all_objects.filter(brokerage=brokerage)
            )
            self.fields['insurer'].queryset = (
                self.fields['insurer'].queryset.model.all_objects.filter(brokerage=brokerage)
            )
            self.fields['branch'].queryset = Branch.all_objects.filter(brokerage=brokerage)
            self.fields['coverages'].queryset = Coverage.all_objects.filter(brokerage=brokerage)
            self.fields['covered_items'].queryset = CoveredItem.all_objects.filter(
                brokerage=brokerage
            )
        else:
            for field_name in ('client', 'insurer', 'branch', 'coverages', 'covered_items'):
                self.fields[field_name].queryset = self.fields[field_name].queryset.none()
