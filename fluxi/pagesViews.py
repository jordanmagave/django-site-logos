# /fluxi/pagesViews.py

import traceback
import json
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
        telefone = data.get("phone") or data.get("telefone")
        captured_url = data.get("url")

        # Validação básica para garantir que os campos obrigatórios estejam presentes no payload do webhook
        if not all([nome, email, telefone, captured_url]):
            error_message = f"Webhook rejeitado. Campos obrigatórios faltando: nome={nome}, email={email}, telefone={telefone}, captured_url={captured_url}"
            logger.error(error_message)
            return JsonResponse(
                {"error": error_message},
                status=400,
            )

        anonymous_id = None
        # 1. O Leadster envia a URL no campo "url", não "captured_url".

        if captured_url:
            parsed_url = urlparse(captured_url)
            query_params = parse_qs(parsed_url.query)
            segment_id_list = query_params.get("segment_anonymous_id")
            if segment_id_list:
                anonymous_id = segment_id_list[0]

        # 2. Extrai os dados do lead e os UTMs diretamente dos campos do JSON.
        utm_source = data.get("utm_source")
        utm_medium = data.get("utm_medium")
        utm_content = data.get("utm_content")
        utm_campaign = data.get("utm_campaing")
        ip_lead = data.get("ip_lead")
        fbclid = data.get("fbclid")
        gclid = data.get("gclid")
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
            gclid=gclid,
            lead_source=lead_source,
            consentimento_analytics=True,  # Assume consentimento via webhook
        )

        # Chamada Identify: Cria ou atualiza o perfil do usuário no Segment
        analytics.identify(
            user_id=email,
            traits={"name": nome, "email": email, "phone": telefone},
            context={"anonymousId": anonymous_id},
        )

        # Chamada Track: Dispara o evento "Lead" com todas as propriedades
        analytics.track(
            user_id=email,
            event="Lead",
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
                "lead_source": lead_source,
            },
            context={"anonymousId": anonymous_id},
        )

        return JsonResponse({"status": "success"}, status=200)

    except Exception as e:
        error_details = traceback.format_exc()
        print(f"Erro no webhook do Leadster: {error_details}")
        return JsonResponse(
            {"error": "Ocorreu um erro interno no servidor.", "details": error_details},
            status=500,
        )
