from django.contrib import admin
from .models import Contato, AuditFinding


@admin.register(AuditFinding)
class AuditFindingAdmin(admin.ModelAdmin):
    """Findings do Site Audit (Semrush) para medir evolução entre exports."""

    list_display = ("import_date", "issue", "count", "page_url", "source")
    list_filter = ("import_date", "issue", "source")
    search_fields = ("page_url", "issue")
    date_hierarchy = "import_date"


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
