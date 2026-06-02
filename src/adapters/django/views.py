"""Adapters Django: views refatoradas que usam os use cases.

Mantém exata compatibilidade de rotas, templates e contextos
com as views legadas em fluxi/pagesViews.py e fluxi/homeViews.py.
"""

from __future__ import annotations

import json
import logging

from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from fluxi.forms import ContatoForm
from src.adapters.django.repository import DjangoOrmLeadRepository
from src.adapters.segment import SegmentCDP
from src.adapters.segment import init as segment_init
from src.adapters.stdlib import SystemClock, UuidIdGenerator
from src.ports.leads import GeoIPPort
from src.use_cases.ingest_leadster_webhook import IngestLeadsterWebhook
from src.use_cases.submit_contact_form import SubmitContactForm

logger = logging.getLogger(__name__)


# ---- Inicialização dos adapters (singletons) ----
_segment_cdp = SegmentCDP()
_system_clock = SystemClock()
_uuid_gen = UuidIdGenerator()
_orm_repo = DjangoOrmLeadRepository()


def _init_segment() -> None:
    segment_init(settings.SEGMENT_WRITE_KEY)


# =========================================================================
# Webhook Leadster
# =========================================================================


@csrf_exempt
@require_POST
def leadster_webhook(request: HttpRequest) -> JsonResponse:
    """Recebe o webhook do Leadster, processa via use case e retorna JSON."""
    _init_segment()

    use_case = IngestLeadsterWebhook(
        repo=_orm_repo,
        cdp=_segment_cdp,
        clock=_system_clock,
        id_gen=_uuid_gen,
        geo=_try_geoip(),
    )

    try:
        body_bytes = request.body
        data = json.loads(body_bytes) if body_bytes else {}
    except json.JSONDecodeError:
        return JsonResponse({"error": "Payload JSON inválido"}, status=400)

    # HMAC signature (futuro: extrair do header X-Leadster-Signature)
    signature = request.META.get("HTTP_X_LEADSTER_SIGNATURE")

    result = use_case.execute(data, signature=signature, body_bytes=request.body)

    if result.is_ok():
        logger.info(f"Webhook processado com sucesso: {data.get('name') or data.get('nome')}")
        return JsonResponse({"status": "success"}, status=200)
    else:
        logger.error(f"Webhook rejeitado: {result.error}")
        return JsonResponse({"error": result.error}, status=400)


def _try_geoip() -> GeoIPPort | None:
    """Tenta carregar o reader GeoIP2. Retorna None se falhar."""
    try:
        import geoip2.database

        from src.adapters.geoip import MaxMindGeoIP

        db_path = settings.BASE_DIR / "geoip" / "GeoLite2-City.mmdb"
        reader = geoip2.database.Reader(str(db_path))
        return MaxMindGeoIP(reader)
    except Exception:
        logger.warning("GeoIP2 nao disponivel — enriquecimento geografico desabilitado")
        return None


# =========================================================================
# Página de contato (formulário)
# =========================================================================


def contato(request: HttpRequest) -> HttpResponse:
    """Renderiza e processa o formulário de contato usando use case."""
    _init_segment()
    use_case = SubmitContactForm(repo=_orm_repo, cdp=_segment_cdp, clock=_system_clock)

    if request.method == "POST":
        form = ContatoForm(request.POST)
        if form.is_valid():
            tracking_from_session = _extract_tracking_from_session(request)
            consent = form.cleaned_data.get("ketch_consent") == "true"

            result = use_case.execute(
                nome=form.cleaned_data["nome"],
                email=form.cleaned_data["email"],
                telefone=form.cleaned_data["telefone"],
                consentimento=consent,
                tracking_params=tracking_from_session,
                ip=request.META.get("REMOTE_ADDR"),
                captured_url=request.build_absolute_uri(),
            )

            if result.is_ok():
                logger.info(f"Contato salvo: {form.cleaned_data['email']}")
                request.session.save()
                return redirect("contato")

        # form inválido ou use case falhou: renderiza com erros
    else:
        form = ContatoForm()

    context = {
        "footer": "true",
        "header": "true",
        "form": form,
        "page_title": "Contato - Centro Educacional Logos",
        "page_description": (
            "Entre em contato com o Centro Educacional Logos em Ananindeua."
            " Agende uma visita e conheça nossa estrutura completa."
        ),
        "page_canonical": "https://www.celogos.com.br/contato/",
        "breadcrumb_items": [
            {"name": "Contato", "url": "https://www.celogos.com.br/contato/"},
        ],
    }
    return render(request, "pages/contato.html", context)


# =========================================================================
# Helpers
# =========================================================================


_TRACKING_KEYS = [
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "gclid",
    "fbclid",
]


def _extract_tracking_from_session(request: HttpRequest) -> dict[str, str]:
    """Extrai parâmetros de tracking da sessão do Django."""
    params: dict[str, str] = {}
    for key in _TRACKING_KEYS:
        val = request.session.get(key)
        if val:
            params[key] = val
    return params
