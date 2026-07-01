# seo/management/commands/seo_import_semrush.py
import csv
import re
from datetime import date, datetime
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from seo.models import AuditFinding


class Command(BaseCommand):
    help = "Importa um export CSV do Site Audit do Semrush para AuditFinding."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", type=str, help="Caminho do CSV do Semrush")
        parser.add_argument(
            "--date",
            type=str,
            default=None,
            help="Data do import (YYYY-MM-DD). Padrão: extraída do nome do arquivo ou hoje.",
        )

    def handle(self, *args, **options):
        path = Path(options["csv_path"])
        if not path.exists():
            raise CommandError(f"Arquivo não encontrado: {path}")

        import_date = self._resolve_date(options["date"], path.name)

        created = 0
        with path.open(encoding="utf-8-sig", newline="") as fh:
            reader = csv.reader(fh)
            header = next(reader)
            issue_cols = header[1:]  # a 1ª coluna é a Page URL
            for row in reader:
                if not row:
                    continue
                page_url = row[0]
                for idx, issue in enumerate(issue_cols, start=1):
                    if idx >= len(row):
                        continue
                    try:
                        count = int(row[idx])
                    except (ValueError, TypeError):
                        continue
                    if count <= 0:
                        continue
                    _, was_created = AuditFinding.objects.update_or_create(
                        source="semrush",
                        import_date=import_date,
                        page_url=page_url,
                        issue=issue,
                        defaults={"count": count},
                    )
                    created += int(was_created)

        total = AuditFinding.objects.filter(import_date=import_date).count()
        self.stdout.write(
            self.style.SUCCESS(
                f"Import {import_date}: {created} novos findings ({total} no total nesta data)."
            )
        )

    def _resolve_date(self, explicit, filename):
        if explicit:
            return datetime.strptime(explicit, "%Y-%m-%d").date()
        m = re.search(r"(\d{8})", filename)
        if m:
            return datetime.strptime(m.group(1), "%Y%m%d").date()
        return date.today()
