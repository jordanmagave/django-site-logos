from datetime import date
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.db.models import Sum
from django.test import TestCase

from seo.models import AuditFinding

FIXTURE = (
    Path(settings.BASE_DIR)
    / "seo"
    / "tests"
    / "fixtures"
    / "semrush_sample_20260701.csv"
)


class ImportSemrushTest(TestCase):
    def test_import_creates_findings_only_for_nonzero(self):
        call_command("seo_import_semrush", str(FIXTURE), stdout=StringIO())
        # 5 findings: (home: title, uncompressed) + (about: title, uncompressed, images)
        self.assertEqual(AuditFinding.objects.count(), 5)
        # zeros não viram finding
        self.assertFalse(
            AuditFinding.objects.filter(
                page_url="https://celogos.com.br/",
                issue="Broken internal images",
            ).exists()
        )

    def test_import_totals_and_date_from_filename(self):
        call_command("seo_import_semrush", str(FIXTURE), stdout=StringIO())
        uncompressed = AuditFinding.objects.filter(
            issue="Uncompressed JavaScript and CSS files"
        ).aggregate(t=Sum("count"))["t"]
        self.assertEqual(uncompressed, 32)
        self.assertEqual(
            AuditFinding.objects.first().import_date, date(2026, 7, 1)
        )

    def test_reimport_is_idempotent(self):
        call_command("seo_import_semrush", str(FIXTURE), stdout=StringIO())
        call_command("seo_import_semrush", str(FIXTURE), stdout=StringIO())
        self.assertEqual(AuditFinding.objects.count(), 5)
