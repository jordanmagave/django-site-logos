"""Caso de uso: submissão do formulário de contato (server-side).

Recebe dados validados do ContatoForm Django e orquestra:
1. Cria entidade Lead
2. Enriquece com tracking params da sessão
3. Persiste via LeadRepositoryPort
4. (Future) Envia evento para CDP
"""

from __future__ import annotations

import logging
from typing import Any

from src.domain.leads.entities import GeoLocation, Lead
from src.domain.leads.value_objects import Email, Phone, TrackingParams
from src.domain.result import Result, error_result, ok_result
from src.ports.leads import CDPPort, ClockPort, LeadRepositoryPort

logger = logging.getLogger(__name__)


class SubmitContactForm:
    """Caso de uso para submissão do formulário de contato."""

    def __init__(self, repo: LeadRepositoryPort, cdp: CDPPort, clock: ClockPort) -> None:
        self._repo = repo
        self._cdp = cdp
        self._clock = clock

    def execute(
        self,
        nome: str,
        email: str,
        telefone: str,
        consentimento: bool,
        tracking_params: dict[str, Any] | None = None,
        ip: str | None = None,
        captured_url: str | None = None,
    ) -> Result[Lead]:
        """Processa a submissão do formulário de contato.

        Args:
            nome: nome do lead
            email: email do lead
            telefone: telefone do lead
            consentimento: se consentiu analytics
            tracking_params: dict com parâmetros de tracking (da sessão)
            ip: endereço IP do lead
            captured_url: URL onde o formulário foi submetido
        """
        try:
            if not nome:
                return error_result("Nome é obrigatório")
            if not email:
                return error_result("Email é obrigatório")

            try:
                email_vo = Email(email)
                phone_vo = Phone(telefone) if telefone else None
            except Exception as exc:
                return error_result(f"Dados inválidos: {exc}")

            tracking = TrackingParams.from_mapping(tracking_params or {})

            lead = Lead(
                nome=nome,
                email=email_vo,
                telefone=phone_vo,
                tracking=tracking,
                captured_url=captured_url,
                ip_lead=ip,
                consentimento_analytics=consentimento,
                location=GeoLocation(),
            )

            self._repo.save(lead)

            return ok_result(lead)

        except Exception as exc:
            logger.exception("Erro no submit_contact_form")
            return error_result(f"Erro interno: {exc}")
