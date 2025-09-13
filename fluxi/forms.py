from django import forms
from .models import Contato


class ContatoForm(forms.ModelForm):
    ketch_consent = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Contato
        fields = ["nome", "email", "telefone"]
        widgets = {
            "nome": forms.TextInput(
                attrs={
                    "class": "single-input-area form-control",
                    "placeholder": "Nome",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "single-input-area form-control mask-email",
                    "placeholder": "Email",
                }
            ),
            "telefone": forms.TextInput(
                attrs={
                    "class": "single-input-area form-control mask-phone ",
                    "placeholder": "(91) 99999-9999",
                }
            ),
        }
