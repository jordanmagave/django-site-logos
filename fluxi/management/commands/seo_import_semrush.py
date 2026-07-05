# fluxi/management/commands/seo_import_semrush.py
"""Importa um export do Site Audit do Semrush (CSV) para o model ``AuditFinding``.

Uso:
    python manage.py seo_import_semrush "celogos.com.br_mega_export_YYYYMMDD.csv"

A data é extraída do nome do arquivo (``YYYYMMDD``) ou passada com ``--date``.
Cria uma linha por célula com contagem > 0 (URL × issue). Idempotente
(``update_or_create``): reimportar a mesma data não duplica.
"""

import csv
import datetime as dt
import re
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from fluxi.models import AuditFinding


class Command(BaseCommand):
    help = "Importa o CSV do Site Audit do Semrush para AuditFinding."

    def add_arguments(self, parser):
        parser.add_argument("csv_path", help="Caminho do CSV exportado do Semrush.")
        parser.add_argument(
            "--date",
            dest="date",
            default=None,
            help="Data do audit (YYYY-MM-DD). Padrão: extraída do nome ou hoje.",
        )
        parser.add_argument("--source", default="semrush")

    def _resolve_date(self, csv_path, arg_date):
        if arg_date:
            return dt.date.fromisoformat(arg_date)
        m = re.search(r"(\d{8})", Path(csv_path).name)
        if m:
            return dt.datetime.strptime(m.group(1), "%Y%m%d").date()
        return dt.date.today()

    def handle(self, *args, **options):
        csv_path = Path(options["csv_path"])
        if not csv_path.exists():
            raise CommandError(f"CSV não encontrado: {csv_path}")
        import_date = self._resolve_date(str(csv_path), options["date"])
        source = options["source"]

        created = updated = 0
        with csv_path.open(encoding="utf-8-sig", newline="") as fh:
            reader = csv.reader(fh)
            header = next(reader, None)
            if not header:
                raise CommandError("CSV vazio.")
            issues = header[1:]  # primeira coluna = Page URL
            for row in reader:
                if not row:
                    continue
                page_url = row[0].strip()
                if not page_url:
                    continue
                for issue, cell in zip(issues, row[1:]):
                    try:
                        count = int((cell or "0").strip() or 0)
                    except ValueError:
                        continue
                    if count <= 0:
                        continue
                    _, was_created = AuditFinding.objects.update_or_create(
                        source=source,
                        import_date=import_date,
                        page_url=page_url,
                        issue=issue.strip(),
                        defaults={"count": count},
                    )
                    created += was_created
                    updated += not was_created

        self.stdout.write(
            self.style.SUCCESS(
                f"Audit {import_date}: {created} criados, {updated} atualizados."
            )
        )
