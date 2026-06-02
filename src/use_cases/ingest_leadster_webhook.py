"""Caso de uso: ingestão de lead do webhook Leadster.

Orquestra:
1. Verificação de assinatura HMAC (se configurada)
2. Validação do payload
3. Criação da entidade Lead com tracking params enriquecidos
4. Enriquecimento GeoIP
5. Persistência via LeadRepositoryPort
6. Eventos Identify + Track via CDPPort
"""

from __future__ import annotations

import logging
from typing import Any

from src.domain.leads.entities import GeoLocation, Lead
from src.domain.leads.value_objects import Email, Phone, TrackingParams
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


class IngestLeadsterWebhook:
    """Caso de uso para processar webhook do Leadster."""

    def __init__(
        self,
        repo: LeadRepositoryPort,
        cdp: CDPPort,
        clock: ClockPort,
        id_gen: IdGeneratorPort,
        geo: GeoIPPort | None = None,
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

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

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
            # 1. HMAC
            hmac_result = self._verify_hmac(signature, body_bytes)
            if hmac_result is not None:
                return hmac_result

            # 2. Validação de payload
            valid = self._validate_payload(payload)
            if valid is not None:
                return valid
            nome, email_str, telefone_str, captured_url = self._extract_fields(payload)

            # 3. Value objects
            try:
                email_vo = Email(email_str)
            except Exception as exc:
                return error_result(f"Email inválido: {exc}")
            phone_vo = Phone(telefone_str) if telefone_str else None

            # 4. Tracking
            now_ms = self._clock.now_ms()
            tracking = self._merge_tracking(payload, captured_url, now_ms)

            # 5. GeoIP
            ip_lead = self._get_str(payload, "ip_lead")
            location = self._resolve_location(ip_lead)

            # 6. Criar entidade
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

            # 7. Persistir
            self._repo.save(lead)

            # 8. CDP
            self._dispatch_to_cdp(lead, tracking, ip_lead)

            return ok_result(lead)

        except Exception as exc:
            logger.exception("Erro inesperado no webhook")
            return error_result(f"Erro interno: {exc}")

    # ------------------------------------------------------------------
    # Etapas internas do pipeline (extraídas para reduzir C901)
    # ------------------------------------------------------------------

    def _verify_hmac(self, signature: str | None, body_bytes: bytes | None) -> Result[Lead] | None:
        """Retorna um Result de erro se HMAC falhar, ou None se ok/skip."""
        if not self._hmac_secret or not self._verifier:
            return None  # HMAC não configurado, skip
        if not signature or not body_bytes:
            return error_result("Assinatura HMAC exigida mas ausente")
        if not self._verifier.verify(body_bytes, signature, self._hmac_secret):
            return error_result("Assinatura HMAC inválida — webhook rejeitado")
        return None

    def _validate_payload(self, payload: dict[str, Any]) -> Result[Lead] | None:
        """Valida campos obrigatórios. Retorna Result de erro ou None."""
        nome = self._get_str(payload, "name", "nome")
        email = self._get_str(payload, "email")
        telefone = self._get_str(payload, "phone", "telefone")
        url = self._get_str(payload, "url")
        if not nome:
            return error_result("Campos obrigatorios ausentes: name/nome")
        if not email:
            return error_result("Campos obrigatorios ausentes: email")
        if not telefone:
            return error_result("Campos obrigatorios ausentes: phone/telefone")
        if not url:
            return error_result("Campos obrigatorios ausentes: url")
        return None

    def _extract_fields(self, payload: dict[str, Any]) -> tuple[str, str, str | None, str]:
        """Extrai campos do payload (ja validado)."""
        return (
            payload.get("name") or payload.get("nome", ""),
            payload.get("email", ""),
            payload.get("phone") or payload.get("telefone"),
            payload.get("url", ""),
        )

    def _merge_tracking(self, payload: dict[str, Any], url: str, now_ms: int) -> TrackingParams:
        """Faz merge de tracking params da URL + payload."""
        url_tracking = TrackingParams.from_url(url, now_ms=now_ms)
        payload_tracking = TrackingParams.from_mapping(payload, now_ms=now_ms, url=url)
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
        return TrackingParams(**merged)

    def _resolve_location(self, ip_lead: str | None) -> GeoLocation:
        if not ip_lead or not self._geo:
            return GeoLocation()
        geo_loc = self._geo.lookup(ip_lead)
        return geo_loc or GeoLocation()

    def _dispatch_to_cdp(self, lead: Lead, tracking: TrackingParams, ip_lead: str | None) -> None:
        user_id = lead.email.value
        context: dict[str, object] = {}
        if tracking.anonymous_id:
            context["anonymousId"] = tracking.anonymous_id
        if ip_lead:
            context["ip"] = ip_lead

        # Identify
        self._cdp.identify(
            user_id=user_id,
            traits={
                "name": lead.nome,
                "email": lead.email.value,
                "phone": lead.telefone.digits if lead.telefone else None,
            },
            context=context,
        )

        # Track
        loc = lead.location
        self._cdp.track(
            user_id=user_id,
            event="Lead",
            properties={
                "name": lead.nome,
                "email": lead.email.value,
                "phone": lead.telefone.digits if lead.telefone else None,
                "captured_url": lead.captured_url,
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
                    "city": loc.city,
                    "region": loc.region,
                    "country": loc.country,
                    "latitude": loc.latitude,
                    "longitude": loc.longitude,
                },
            },
            context=context,
            message_id=self._id_gen.generate(),
        )

    @staticmethod
    def _get_str(data: dict[str, Any], *keys: str) -> str | None:
        for k in keys:
            v = data.get(k)
            if v not in (None, ""):
                return str(v).strip()
        return None
