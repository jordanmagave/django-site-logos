from django import forms
from .models import agendarVisita


class CaptacaoContatoForm(forms.ModelForm):
    class Meta:
        model = agendarVisita
        fields = ["nome", "email", "telefone"]
