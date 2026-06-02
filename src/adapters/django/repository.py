"""Adaptador Django ORM para LeadRepositoryPort.

Mapeia entre a entidade de domínio Lead e o modelo Django Contato.
"""

from __future__ import annotations

import logging

from fluxi.models import Contato
from src.domain.leads.entities import Lead

logger = logging.getLogger(__name__)


class DjangoOrmLeadRepository:
    """Implementa LeadRepositoryPort usando Contato.objects do Django ORM."""

    def save(self, lead: Lead) -> None:
        tracking = lead.tracking
        Contato.objects.create(
            nome=lead.nome,
            email=lead.email.value,
            telefone=lead.telefone.digits if lead.telefone else "",
            captured_url=lead.captured_url or "",
            ip_lead=lead.ip_lead,
            consentimento_analytics=lead.consentimento_analytics,
            lead_source=tracking.lead_source,
            utm_source=tracking.utm_source,
            utm_medium=tracking.utm_medium,
            utm_campaign=tracking.utm_campaign,
            utm_term=tracking.utm_term,
            utm_content=tracking.utm_content,
            gclid=tracking.gclid,
            fbclid=tracking.fbclid,
            fbp=tracking.fbp,
            fbc=tracking.fbc,
        )

    def exists_by_email(self, email: str) -> bool:
        return Contato.objects.filter(email=email).exists()
