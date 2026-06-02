"""Fakes (implementações em memória) para todos os ports.

Usados em testes de use_cases e integração.
"""

from __future__ import annotations

from src.domain.leads.entities import GeoLocation, Lead


class FakeLeadRepository:
    """Armazena leads em memória (dict).

    Permite inspecionar e limpar estado durante testes.
    """

    def __init__(self) -> None:
        self._leads: list[Lead] = []
        self._emails: set[str] = set()

    def save(self, lead: Lead) -> None:
        self._leads.append(lead)
        self._emails.add(lead.email.value)

    def exists_by_email(self, email: str) -> bool:
        return email in self._emails

    @property
    def saved_leads(self) -> list[Lead]:
        return list(self._leads)

    def clear(self) -> None:
        self._leads.clear()
        self._emails.clear()


class FakeCDP:
    """Acumula chamadas identify / track em listas.

    permite inspecionar chamadas após cada operação.
    """

    def __init__(self) -> None:
        self.identify_calls: list[dict[str, object]] = []
        self.track_calls: list[dict[str, object]] = []

    def identify(
        self, user_id: str, traits: dict[str, object], context: dict[str, object] | None = None
    ) -> None:
        self.identify_calls.append({"user_id": user_id, "traits": traits, "context": context})

    def track(
        self,
        user_id: str,
        event: str,
        properties: dict[str, object] | None = None,
        context: dict[str, object] | None = None,
        message_id: str | None = None,
        timestamp: str | None = None,
    ) -> None:
        self.track_calls.append(
            {
                "user_id": user_id,
                "event": event,
                "properties": properties,
                "context": context,
                "message_id": message_id,
                "timestamp": timestamp,
            }
        )

    def clear(self) -> None:
        self.identify_calls.clear()
        self.track_calls.clear()


class FakeClock:
    """Retorna timestamp fixo configurável."""

    def __init__(self, now_ms: int = 1_700_000_000_000) -> None:
        self._now_ms = now_ms

    def now_ms(self) -> int:
        return self._now_ms

    def set(self, now_ms: int) -> None:
        self._now_ms = now_ms


class FakeIdGenerator:
    """Retorna um ID fixo ou próximo de uma lista."""

    def __init__(self, *ids: str) -> None:
        self._ids = list(ids) or ["fake-id-001"]
        self._index = 0

    def generate(self) -> str:
        if self._index < len(self._ids):
            val = self._ids[self._index]
            self._index += 1
            return val
        return f"fake-id-auto-{self._index}"


class FakeWebhookVerifier:
    """Sempre aprova ou rejeita conforme configurado."""

    def __init__(self, approved: bool = True) -> None:
        self._approved = approved

    def verify(self, payload: bytes, signature: str, secret: str) -> bool:
        return self._approved


class FakeGeoIP:
    """Retorna localização mockada ou None."""

    def __init__(
        self, location: GeoLocation = GeoLocation(city="Belem", region="PA", country="BR")
    ) -> None:
        self._location = location

    def lookup(self, ip: str) -> GeoLocation | None:
        if ip in ("", "127.0.0.1", "0.0.0.0"):
            return None
        return self._location
