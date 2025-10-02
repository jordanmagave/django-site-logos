# /fluxi/pagesViews.py

import traceback
import json
import re
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
import segment.analytics as analytics
from .forms import ContatoForm
from .models import Contato
from urllib.parse import urlparse, parse_qs
import logging
from datetime import datetime, timezone
import time


# Configura um logger para ajudar a depurar
logger = logging.getLogger(__name__)


def about(request):
    """Renderiza a página sobre nós."""
    data = {"footer": "true"}
    return render(request, "pages/about.html", data)


def contato(request):
    """Renderiza e processa o formulário de contato."""
    if request.method == "POST":
        form = ContatoForm(request.POST)
        if form.is_valid():
            instancia_contato = form.save(commit=False)

            consent_given = form.cleaned_data.get("ketch_consent") == "true"
            instancia_contato.consentimento_analytics = consent_given
            # --- Captura dos Parâmetros de Rastreamento ---
            tracking_params_keys = [
                "utm_source",
                "utm_medium",
                "utm_campaign",
                "utm_term",
                "utm_content",
                "gclid",
                "fbclid",
            ]

            for key in tracking_params_keys:
                if key in request.session:
                    # Salva o valor da sessão no campo correspondente do modelo
                    setattr(instancia_contato, key, request.session.get(key))

            # Agora, salva a instância completa no banco de dados
            instancia_contato.save()
            logger.info(
                f"Contato salvo no banco de dados com consentimento: {consent_given}"
            )

            request.session.save()  # Certifique-se de que a sessão está salva

            return redirect("contato")
    else:
        form = ContatoForm()

    context = {
        "footer": "true",
        "header": "true",
        "form": form,
    }
    return render(request, "pages/contato.html", context)


analytics.write_key = settings.SEGMENT_WRITE_KEY


@csrf_exempt
@require_POST
def leadster_webhook(request):
    """
    Recebe o webhook do Leadster, processa os dados recebidos,
    salva o lead e envia os eventos para o Segment.
    """
    try:
        # O payload do Leadster é o próprio objeto de dados.
        data = json.loads(request.body)
        logger.info(f"Payload final recebido e processado: {data}")

        # Verifica se o corpo do webhook está vazio ou não contém os dados esperados e retorna um erro apropriado se necessário.
        if not data:
            return JsonResponse(
                {"error": "Chave 'body' não encontrada no payload."}, status=400
            )

        # Extrai os dados principais do lead
        nome = data.get("name") or data.get("nome")
        email = data.get("email")
        telefone_original = data.get("phone") or data.get("telefone")
        captured_url = data.get("url")

        # Validação básica para garantir que os campos obrigatórios estejam presentes no payload do webhook
        if not all([nome, email, telefone_original, captured_url]):
            error_message = f"Webhook rejeitado. Campos obrigatórios faltando: nome={nome}, email={email}, telefone={telefone_original}, captured_url={captured_url}"
            logger.error(error_message)
            return JsonResponse(
                {"error": error_message},
                status=400,
            )

        telefone = None
        if telefone_original:
            # Remove todos os caracteres que não são dígitos
            telefone = re.sub(r"\D", "", telefone_original)

        anonymous_id = None
        parsed_url = urlparse(captured_url)
        query_params = parse_qs(parsed_url.query)

        # 1. Extrai os dados do lead dos parâmetros de URL, se disponíveis.
        fbp = query_params.get("fbp", [None])[
            0
        ]  # Exemplo: "fb.1.1234567890.1234567890"
        fbc = query_params.get("fbc", [None])[0]
        fbclid = query_params.get("fbclid", [None])[0]  # Exemplo: "IwAR1..."
        gclid = query_params.get("gclid", [None])[0]  # Exemplo: "EAIaIQobChMI..."
        # Define o anonymous_id a partir do Segment, se disponível
        anonymous_id = query_params.get("segment_anonymous_id", [None])[0]

        if not fbc and fbclid:
            # "subdomain" é 1 para 'site.com' e 2 para 'www.site.com'
            subdomain_index = 2 if parsed_url.netloc.startswith("www.") else 1
            creation_time = int(time.time() * 1000)  # Tempo atual em milissegundos

            fbc = f"fb.{subdomain_index}.{creation_time}.{fbclid}"  # Exemplo: "fb.1.1234567890.IwAR1..."

        # 2. Extrai os dados do lead e os UTMs diretamente dos campos do JSON.
        utm_source = data.get("utm_source")
        utm_medium = data.get("utm_medium")
        utm_content = data.get("utm_content")
        utm_campaign = data.get("utm_campaing")
        ip_lead = data.get("ip_lead")
        lead_source = data.get("lead_source")

        # Crie e salve a instância do Contato no banco de dados
        Contato.objects.create(
            nome=nome,
            email=email,
            telefone=telefone,
            utm_source=utm_source,
            utm_medium=utm_medium,
            utm_content=utm_content,
            utm_campaign=utm_campaign,
            captured_url=captured_url,
            ip_lead=ip_lead,
            fbclid=fbclid,
            fbp=fbp,
            fbc=fbc,
            gclid=gclid,
            lead_source=lead_source,
            consentimento_analytics=True,  # Assume consentimento via webhook
        )

        # Chamada Identify: Cria ou atualiza o perfil do usuário no Segment
        analytics.identify(
            user_id=email,
            traits={"name": nome, "email": email, "phone": telefone, "ip": ip_lead},
            context={"anonymousId": anonymous_id, "ip": ip_lead},
        )

        # Chamada Track: Dispara o evento "Lead" com todas as propriedades
        analytics.track(
            user_id=email,
            event="Lead",
            timestamp=datetime.now(timezone.utc),
            properties={
                "name": nome,
                "email": email,
                "phone": telefone,
                "captured_url": captured_url,
                "utm_source": utm_source,
                "utm_medium": utm_medium,
                "utm_content": utm_content,
                "utm_campaign": utm_campaign,
                "ip_lead": ip_lead,
                "gclid": gclid,
                "fbclid": fbclid,
                "fbp": fbp,
                "fbc": fbc,
                "lead_source": lead_source,
            },
            context={"anonymousId": anonymous_id},
        )

        return JsonResponse({"status": "success"}, status=200)

    except Exception:
        error_details = traceback.format_exc()
        print(f"Erro no webhook do Leadster: {error_details}")
        return JsonResponse(
            {"error": "Ocorreu um erro interno no servidor.", "details": error_details},
            status=500,
        )
