"""Testes adicionais para cobrir linhas restantes do webhook use case."""

from __future__ import annotations

import pytest

from src.adapters.fakes import (
    FakeCDP,
    FakeClock,
    FakeIdGenerator,
    FakeLeadRepository,
    FakeWebhookVerifier,
)
from src.use_cases.ingest_leadster_webhook import IngestLeadsterWebhook


class TestIngestLeadsterWebhookEdgeCases:
    """Testes para branches nao cobertas pelo test principal."""

    @pytest.fixture
    def base_uc(self) -> IngestLeadsterWebhook:
        return IngestLeadsterWebhook(
            repo=FakeLeadRepository(),
            cdp=FakeCDP(),
            clock=FakeClock(),
            id_gen=FakeIdGenerator(),
            geo=None,  # sem GeoIP
            verifier=None,
            hmac_secret=None,
        )

    def test_rejeita_hmac_quando_exigido_mas_sem_signature(self) -> None:
        uc = IngestLeadsterWebhook(
            repo=FakeLeadRepository(),
            cdp=FakeCDP(),
            clock=FakeClock(),
            id_gen=FakeIdGenerator(),
            geo=None,
            verifier=FakeWebhookVerifier(approved=True),
            hmac_secret="secret",
        )
        payload = {
            "name": "Test",
            "email": "test@hmac.com",
            "phone": "(91) 99999-9999",
            "url": "https://site.com",
        }
        # Sem signature e body_bytes
        result = uc.execute(payload)
        assert result.is_error()
        assert "ausente" in result.error

    def test_rejeita_hmac_sem_body_bytes(self) -> None:
        uc = IngestLeadsterWebhook(
            repo=FakeLeadRepository(),
            cdp=FakeCDP(),
            clock=FakeClock(),
            id_gen=FakeIdGenerator(),
            geo=None,
            verifier=FakeWebhookVerifier(approved=True),
            hmac_secret="secret",
        )
        payload = {
            "name": "Test",
            "email": "test@hmac.com",
            "phone": "(91) 99999-9999",
            "url": "https://site.com",
        }
        result = uc.execute(payload, signature="some-sig")
        assert result.is_error()
        assert "ausente" in result.error

    def test_funciona_sem_geoip(self, base_uc: IngestLeadsterWebhook) -> None:
        payload = {
            "nome": "SemGeo",
            "email": "semgeo@test.com",
            "telefone": "(91) 99999-9999",
            "url": "https://site.com",
            "ip_lead": "8.8.8.8",
        }
        result = base_uc.execute(payload)
        assert result.is_ok(), f"Esperado sucesso: {result.error}"

    def test_funciona_com_nome_as_name(self) -> None:
        uc = IngestLeadsterWebhook(
            repo=FakeLeadRepository(),
            cdp=FakeCDP(),
            clock=FakeClock(),
            id_gen=FakeIdGenerator(),
            geo=None,
        )
        payload = {
            "name": "UsandoName",
            "email": "namefield@test.com",
            "phone": "(91) 99999-9999",
            "url": "https://site.com",
        }
        result = uc.execute(payload)
        assert result.is_ok()
        assert result.value is not None
        assert result.value.nome == "UsandoName"
