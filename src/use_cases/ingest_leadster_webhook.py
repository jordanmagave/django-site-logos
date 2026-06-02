"""Caso de uso: ingestão de lead do webhook Leadster.

Orquestra:
1. Validação do payload
2. Verificação de assinatura HMAC (se configurada)
3. Criação da entidade Lead com tracking params
4. Enriquecimento GeoIP
5. Persistência via LeadRepositoryPort
6. Eventos Identify + Track via CDPPort
"""

from __future__ import annotations

import json
import logging
from dataclasses import replace
from typing import Any

from src.domain.errors import InvalidLeadPayloadError
from src.domain.leads.entities import GeoLocation, Lead
from src.domain.leads.value_objects import Email, MessageId, Phone, TrackingParams
from src.domain.result import Result, error_result, ok_result
from src.ports.leads import (
    CDPPort,
    ClockPort,
    GeoIPPort,
    IdGeneratorPort,
    LeadRepositoryPort,
    WebhookVerifierPort,
)

logger = logging.getLogger(__name__)

_REQUIRED_FIELDS = ("name", "nome", "email", "phone", "telefone", "url")

# Janela de idempotencia em ms (para MessageId)
_IDEMPOTENCY_WINDOW_MS = 60_000 * 5  # 5 minutos


class IngestLeadsterWebhook:
    """Caso de uso para processar webhook do Leadster."""

    def __init__(
        self,
        repo: LeadRepositoryPort,
        cdp: CDPPort,
        clock: ClockPort,
        id_gen: IdGeneratorPort,
        geo: GeoIPPort,
        verifier: WebhookVerifierPort | None = None,
        hmac_secret: str | None = None,
    ) -> None:
        self._repo = repo
        self._cdp = cdp
        self._clock = clock
        self._id_gen = id_gen
        self._geo = geo
        self._verifier = verifier
        self._hmac_secret = hmac_secret

    def execute(
        self,
        payload: dict[str, Any],
        *,
        signature: str | None = None,
        body_bytes: bytes | None = None,
    ) -> Result[Lead]:
        """Processa o payload do webhook e retorna um Result.

        Args:
            payload: dados do lead (dict)
            signature: assinatura HMAC do header (se houver)
            body_bytes: body raw para verificação HMAC

        Returns:
            Result[Lead] — Ok(lead) em sucesso, Error(msg) em falha
        """
        try:
            # ---- 1. Verificação HMAC (opcional) ----
            if self._hmac_secret and self._verifier:
                if not signature or not body_bytes:
                    return error_result("Assinatura HMAC exigida mas ausente")
                if not self._verifier.verify(body_bytes, signature, self._hmac_secret):
                    return error_result("Assinatura HMAC inválida — webhook rejeitado")

            # ---- 2. Validação de campos obrigatórios ----
            nome = self._get_str(payload, "name", "nome")
            email = self._get_str(payload, "email")
            telefone = self._get_str(payload, "phone", "telefone")
            captured_url = self._get_str(payload, "url")

            if not nome:
                return error_result("Campos obrigatorios ausentes: name/nome")
            if not email:
                return error_result("Campos obrigatorios ausentes: email")
            if not telefone:
                return error_result("Campos obrigatorios ausentes: phone/telefone")
            if not captured_url:
                return error_result("Campos obrigatorios ausentes: url")

            # ---- 3. Value objects ----
            try:
                email_vo = Email(email)
                phone_vo = Phone(telefone) if telefone else None
            except Exception as exc:
                return error_result(f"Dados invalidos: {exc}")

            # ---- 4. Tracking params ----
            now_ms = self._clock.now_ms()
            # Extrai params da URL e do payload; payload sobrescreve URL
            url_tracking = TrackingParams.from_url(captured_url, now_ms=now_ms)
            payload_tracking = TrackingParams.from_mapping(payload, now_ms=now_ms, url=captured_url)
            # Merge manual: payload fields sobrescrevem URL fields quando presentes
            merged = {
                "utm_source": payload_tracking.utm_source or url_tracking.utm_source,
                "utm_medium": payload_tracking.utm_medium or url_tracking.utm_medium,
                "utm_campaign": payload_tracking.utm_campaign or url_tracking.utm_campaign,
                "utm_term": payload_tracking.utm_term or url_tracking.utm_term,
                "utm_content": payload_tracking.utm_content or url_tracking.utm_content,
                "gclid": payload_tracking.gclid or url_tracking.gclid,
                "fbclid": payload_tracking.fbclid or url_tracking.fbclid,
                "gbraid": payload_tracking.gbraid or url_tracking.gbraid,
                "wbraid": payload_tracking.wbraid or url_tracking.wbraid,
                "fbp": payload_tracking.fbp or url_tracking.fbp,
                "fbc": payload_tracking.fbc or url_tracking.fbc,
                "anonymous_id": payload_tracking.anonymous_id or url_tracking.anonymous_id,
                "lead_source": payload_tracking.lead_source or url_tracking.lead_source,
            }
            tracking = TrackingParams(**merged)

            # ---- 5. Enriquecimento GeoIP ----
            ip_lead = self._get_str(payload, "ip_lead")
            location = GeoLocation()
            if ip_lead:
                geo_loc = self._geo.lookup(ip_lead)
                if geo_loc:
                    location = geo_loc

            # ---- 6. Cria entidade Lead ----
            lead = Lead(
                nome=nome,
                email=email_vo,
                telefone=phone_vo,
                tracking=tracking,
                captured_url=captured_url,
                ip_lead=ip_lead,
                consentimento_analytics=True,
                location=location,
            )

            # ---- 7. Persiste ----
            self._repo.save(lead)

            # ---- 8. Dispara eventos CDP ----
            user_id = email_vo.value
            context: dict[str, object] = {}
            if tracking.anonymous_id:
                context["anonymousId"] = tracking.anonymous_id
            if ip_lead:
                context["ip"] = ip_lead

            # Identify
            self._cdp.identify(
                user_id=user_id,
                traits={
                    "name": nome,
                    "email": email_vo.value,
                    "phone": phone_vo.digits if phone_vo else None,
                },
                context=context,
            )

            # Track
            message_id = self._id_gen.generate()
            self._cdp.track(
                user_id=user_id,
                event="Lead",
                properties={
                    "name": nome,
                    "email": email_vo.value,
                    "phone": phone_vo.digits if phone_vo else None,
                    "captured_url": captured_url,
                    "utm_source": tracking.utm_source,
                    "utm_medium": tracking.utm_medium,
                    "utm_campaign": tracking.utm_campaign,
                    "utm_content": tracking.utm_content,
                    "ip_lead": ip_lead,
                    "gclid": tracking.gclid,
                    "fbclid": tracking.fbclid,
                    "fbp": tracking.fbp,
                    "fbc": tracking.fbc,
                    "gbraid": tracking.gbraid,
                    "wbraid": tracking.wbraid,
                    "lead_source": tracking.lead_source,
                    "location": {
                        "city": location.city,
                        "region": location.region,
                        "country": location.country,
                        "latitude": location.latitude,
                        "longitude": location.longitude,
                    },
                },
                context=context,
                message_id=message_id,
                timestamp=str(self._clock.now_ms()),
            )

            return ok_result(lead)

        except Exception as exc:
            logger.exception("Erro inesperado no webhook")
            return error_result(f"Erro interno: {exc}")

    @staticmethod
    def _get_str(data: dict[str, Any], *keys: str) -> str | None:
        for k in keys:
            v = data.get(k)
            if v not in (None, ""):
                return str(v).strip()
            return None
