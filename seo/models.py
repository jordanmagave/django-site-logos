from django.db import models


class AuditFinding(models.Model):
    """Um achado do Site Audit (Semrush) para uma URL, em uma data de import.

    Permite medir a evolução do audit entre exports (baseline -> re-crawl).
    """

    source = models.CharField(max_length=50, default="semrush")
    import_date = models.DateField(db_index=True)
    page_url = models.CharField(max_length=1000)
    issue = models.CharField(max_length=255)
    count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Audit Finding"
        verbose_name_plural = "Audit Findings"
        unique_together = ["source", "import_date", "page_url", "issue"]
        ordering = ["-import_date", "page_url"]
        indexes = [models.Index(fields=["issue"])]

    def __str__(self):
        return f"[{self.import_date}] {self.issue} ({self.count}) - {self.page_url}"
