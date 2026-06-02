"""Portas (Protocols) que o domínio e use_cases dependem.

Cada Protocol define um contrato que será implementado por um adapter
concreto (Django ORM, Segment SDK, MaxMind, etc.).
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from src.domain.leads.entities import GeoLocation, Lead
from src.domain.leads.value_objects import MessageId


@runtime_checkable
class LeadRepositoryPort(Protocol):
    """Persistência de leads."""

    def save(self, lead: Lead) -> None:
        """Persiste um lead."""
        ...

    def exists_by_email(self, email: str) -> bool:
        """Verifica se já existe lead com este e-mail."""
        ...


@runtime_checkable
class CDPPort(Protocol):
    """Envio de eventos para Customer Data Platform (Segment/RudderStack)."""

    def identify(
        self, user_id: str, traits: dict[str, object], context: dict[str, object] | None = None
    ) -> None:
        """Cria ou atualiza perfil do usuário."""
        ...

    def track(
        self,
        user_id: str,
        event: str,
        properties: dict[str, object] | None = None,
        context: dict[str, object] | None = None,
        message_id: str | None = None,
        timestamp: str | None = None,
    ) -> None:
        """Dispara evento com propriedades."""
        ...


@runtime_checkable
class GeoIPPort(Protocol):
    """Resolução de localização a partir de IP."""

    def lookup(self, ip: str) -> GeoLocation | None:
        """Retorna localização para um IP, ou None se não possível."""
        ...


@runtime_checkable
class ClockPort(Protocol):
    """Fonte de tempo (para testabilidade)."""

    def now_ms(self) -> int:
        """Timestamp atual em milissegundos."""
        ...


@runtime_checkable
class IdGeneratorPort(Protocol):
    """Geração de identificadores únicos."""

    def generate(self) -> str:
        """Retorna um ID único."""
        ...


@runtime_checkable
class WebhookVerifierPort(Protocol):
    """Verificação de assinatura HMAC de webhooks."""

    def verify(self, payload: bytes, signature: str, secret: str) -> bool:
        """Retorna True se a assinatura confere."""
        ...
