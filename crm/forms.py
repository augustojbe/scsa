from django import forms

from base.constants import PIPELINE_STAGE_COLORS
from clients.models import Client
from crm.models import Deal, Pipeline, PipelineStage
from policies.models import Proposal


class PipelineForm(forms.ModelForm):
    class Meta:
        model = Pipeline
        fields = ['name', 'is_default']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PipelineStageForm(forms.ModelForm):
    class Meta:
        model = PipelineStage
        fields = ['name', 'color', 'order']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'color': forms.Select(attrs={'class': 'form-select'}),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def __init__(self, *args, brokerage=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.brokerage = brokerage
        self.fields['color'].choices = PIPELINE_STAGE_COLORS


class DealForm(forms.ModelForm):
    class Meta:
        model = Deal
        fields = [
            'pipeline',
            'stage',
            'client',
            'proposal',
            'title',
            'value',
            'expected_close_date',
            'order',
        ]
        widgets = {
            'pipeline': forms.Select(attrs={'class': 'form-select'}),
            'stage': forms.Select(attrs={'class': 'form-select'}),
            'client': forms.Select(attrs={'class': 'form-select'}),
            'proposal': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'value': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.01', 'min': '0'}
            ),
            'expected_close_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'order': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
        }

    def __init__(self, *args, brokerage=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.brokerage = brokerage
        if brokerage is not None:
            self.fields['pipeline'].queryset = Pipeline.all_objects.filter(
                brokerage=brokerage
            )
            self.fields['stage'].queryset = PipelineStage.all_objects.filter(
                brokerage=brokerage
            )
            self.fields['client'].queryset = Client.all_objects.filter(brokerage=brokerage)
            self.fields['proposal'].queryset = Proposal.all_objects.filter(
                brokerage=brokerage
            )
        else:
            for name in ('pipeline', 'stage', 'client', 'proposal'):
                self.fields[name].queryset = self.fields[name].queryset.none()

    def clean(self):
        cleaned_data = super().clean()
        pipeline = cleaned_data.get('pipeline')
        stage = cleaned_data.get('stage')
        if pipeline and stage and stage.pipeline_id != pipeline.pk:
            self.add_error('stage', 'A etapa deve pertencer ao pipeline selecionado.')
        return cleaned_data
