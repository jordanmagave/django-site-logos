# views.py
from django.views.generic import View
from django.shortcuts import render, redirect
from django.http import (
    FileResponse,
    HttpResponseForbidden,
    Http404,
    JsonResponse,
    HttpResponseRedirect,
)
from django.conf import settings
from django.utils import timezone
from django.contrib import messages
import logging
import re

from .models import ResponsavelFinanceiro, LogAcesso, BoletoArquivo
from .services.pdf_manager import PDFManager
from .services.cloud_storage import CloudStorageManager

logger = logging.getLogger("boletos.access")


class ConsultaBoletoView(View):
    def get(self, request):
        return render(request, "boletos/consulta.html")

    def post(self, request):
        cpf = request.POST.get("cpf", "")
        # Remove pontos e traços
        cpf = re.sub(r"\D", "", cpf)

        if not cpf or len(cpf) != 11:
            messages.error(request, "CPF inválido")
            return redirect("boletos:consulta")

        try:
            # Busca alunos do responsável
            responsavel = ResponsavelFinanceiro.objects.filter(cpf=cpf).first()

            if not responsavel:
                messages.warning(request, "CPF não encontrado")
                return redirect("boletos:consulta")

            # Salva CPF na sessão para validação posterior
            request.session["cpf_validado"] = cpf

            # Log de acesso
            LogAcesso.objects.create(
                cpf=cpf, tipo="CONSULTA", ip=request.META.get("REMOTE_ADDR", "")
            )

            # Busca boletos disponíveis
            pdf_manager = PDFManager()
            alunos_com_boletos = pdf_manager.get_boletos_por_responsavel(responsavel)

            return render(
                request,
                "boletos/lista.html",
                {
                    "responsavel": responsavel,
                    "alunos_com_boletos": alunos_com_boletos,
                },
            )

        except Exception as e:
            logger.error(f"Erro na consulta de boletos: {str(e)}")
            messages.error(request, "Erro ao consultar boletos")
            return redirect("boletos:consulta")


class DownloadBoletoView(View):
    def get(self, request, boleto_id):
        cpf = request.session.get("cpf_validado")

        if not cpf:
            return HttpResponseForbidden("Acesso negado")

        try:
            # Busca boleto e valida acesso
            boleto = BoletoArquivo.objects.select_related("aluno__responsavel").get(
                id=boleto_id, aluno__responsavel__cpf=cpf
            )

            # Gera URL temporária
            cloud_manager = CloudStorageManager()
            signed_url = cloud_manager.generate_signed_url(boleto.nome_arquivo)

            # Log de download
            LogAcesso.objects.create(
                cpf=cpf,
                arquivo=boleto.nome_arquivo,
                tipo="DOWNLOAD",
                ip=request.META.get("REMOTE_ADDR", ""),
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )

            # Redireciona para URL temporária
            return HttpResponseRedirect(signed_url)

        except BoletoArquivo.DoesNotExist:
            return Http404("Boleto não encontrado")
