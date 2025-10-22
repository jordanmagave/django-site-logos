# services/pdf_manager.py
import os
from pathlib import Path


class PDFManager:
    def __init__(self, pdf_folder):
        self.pdf_folder = Path(pdf_folder)

    def get_boletos_aluno(self, codigo_aluno):
        # Busca PDFs do aluno
        pattern = f"*{codigo_aluno}*.pdf"
        return list(self.pdf_folder.glob(pattern))

    def get_pdf_info(self, pdf_path):
        # Extrai informações do nome do arquivo
        # Exemplo: BOLETO_202403_12345_30042024.pdf
        # Retorna: mes, codigo_aluno, vencimento
        pass
