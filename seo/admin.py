from django.contrib import admin

from .models import AuditFinding


@admin.register(AuditFinding)
class AuditFindingAdmin(admin.ModelAdmin):
    list_display = ("import_date", "issue", "count", "page_url", "source")
    list_filter = ("import_date", "source", "issue")
    search_fields = ("page_url", "issue")
    date_hierarchy = "import_date"
