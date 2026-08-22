from django import forms

from clients.models import Client, ClientAttachment


class ClientAttachmentForm(forms.ModelForm):
    class Meta:
        model = ClientAttachment
        fields = ['file', 'description']
        widgets = {
            'file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Descrição (opcional)'}
            ),
        }


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'name',
            'document',
            'type',
            'email',
            'phone',
            'street',
            'number',
            'complement',
            'neighborhood',
            'city',
            'state',
            'zip_code',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'document': forms.TextInput(attrs={'class': 'form-control'}),
            'type': forms.Select(attrs={'class': 'form-select'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'street': forms.TextInput(attrs={'class': 'form-control'}),
            'number': forms.TextInput(attrs={'class': 'form-control'}),
            'complement': forms.TextInput(attrs={'class': 'form-control'}),
            'neighborhood': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'zip_code': forms.TextInput(attrs={'class': 'form-control'}),
        }
