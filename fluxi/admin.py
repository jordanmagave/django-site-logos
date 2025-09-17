from django.contrib import admin
from .models import Contato


@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    """Define a exibição do modelo Contato no painel de administração."""

    list_display = ("nome", "email", "telefone", "utm_source", "gclid", "fbclid")
    search_fields = ("nome", "email")
    list_filter = ("utm_source", "utm_medium")
    readonly_fields = (
        "nome",
        "email",
        "telefone",
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_term",
        "utm_content",
        "gclid",
        "fbclid",
    )
