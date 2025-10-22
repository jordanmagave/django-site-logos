# management/commands/migrar_boletos_cloud.py
from django.core.management.base import BaseCommand
from pathlib import Path
import os

from boleto.services.cloud_storage import CloudStorageManager
from boleto.models import Aluno, BoletoArquivo


class Command(BaseCommand):
    help = "Migra boletos locais para Cloud Storage"

    def add_arguments(self, parser):
        parser.add_argument(
            "--pasta-boletos", type=str, help="Caminho da pasta com os PDFs"
        )

    def handle(self, *args, **options):
        pasta = Path(options["pasta_boletos"])
        cloud_manager = CloudStorageManager()

        for pdf_file in pasta.glob("*.pdf"):
            try:
                # Extrai nome do aluno do arquivo
                nome_aluno = pdf_file.stem  # nome sem extensão

                # Busca aluno
                aluno = Aluno.objects.filter(
                    nome__icontains=nome_aluno.split()[0]
                ).first()

                if not aluno:
                    self.stdout.write(
                        self.style.WARNING(f"Aluno não encontrado: {nome_aluno}")
                    )
                    continue

                # Upload para cloud
                self.stdout.write(f"Enviando {pdf_file.name}...")
                url = cloud_manager.upload_pdf(str(pdf_file), pdf_file.name)

                # Registra no banco
                BoletoArquivo.objects.update_or_create(
                    aluno=aluno,
                    nome_arquivo=pdf_file.name,
                    defaults={
                        "url_cloud": url,
                        "tamanho": pdf_file.stat().st_size,
                        "mes_referencia": self.extrair_mes(pdf_file.name),
                    },
                )

                self.stdout.write(self.style.SUCCESS(f"✓ {pdf_file.name}"))

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Erro em {pdf_file.name}: {e}"))

    def extrair_mes(self, nome_arquivo):
        # Implementar lógica para extrair mês do nome
        # Por enquanto, retorna mês atual
        from datetime import datetime

        return datetime.now().strftime("%Y-%m")
