"""Testes RED para o use case ingest_leadster_webhook."""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone

import pytest

from src.adapters.fakes import FakeCDP, FakeClock, FakeGeoIP, FakeIdGenerator, FakeLeadRepository, FakeWebhookVerifier
from src.domain.leads.entities import GeoLocation, Lead
from src.domain.leads.value_objects import Email, Phone, TrackingParams
from src.use_cases.ingest_leadster_webhook import IngestLeadsterWebhook


class TestIngestLeadsterWebhook:
    """RED: testes do caso de uso de ingestão de webhook Leadster."""

    @pytest.fixture
    def use_case(self) -> IngestLeadsterWebhook:
        return IngestLeadsterWebhook(
            repo=FakeLeadRepository(),
            cdp=FakeCDP(),
            clock=FakeClock(now_ms=1_700_000_000_000),
            id_gen=FakeIdGenerator("msg-001"),
            geo=FakeGeoIP(),
            verifier=FakeWebhookVerifier(approved=True),
        )

    def test_rejeita_payload_sem_campos_obrigatorios(self, use_case: IngestLeadsterWebhook) -> None:
        payload: dict = {}
        result = use_case.execute(payload)
        assert result.is_error()
        assert "obrigatorios" in result.error.lower()

    def test_rejeita_quando_nome_ausente(self, use_case: IngestLeadsterWebhook) -> None:
        payload = {"email": "a@b.com", "phone": "(91) 99999-9999", "url": "https://site.com"}
        result = use_case.execute(payload)
        assert result.is_error()

    def test_rejeita_quando_url_ausente(self, use_case: IngestLeadsterWebhook) -> None:
        payload = {"name": "Joao", "email": "a@b.com", "phone": "(91) 99999-9999"}
        result = use_case.execute(payload)
        assert result.is_error()

    def test_cria_lead_com_dados_minimos(self, use_case: IngestLeadsterWebhook) -> None:
        payload = {
            "name": "Joao Silva",
            "email": "joao@example.com",
            "phone": "(91) 99999-9999",
            "url": "https://celogos.com.br/contato",
        }
        result = use_case.execute(payload)
        assert result.is_ok(), f"Esperado sucesso, obteve: {result.error}"
        assert result.value is not None
        lead = result.value
        assert lead.nome == "Joao Silva"
        assert lead.email.value == "joao@example.com"
        assert lead.telefone is not None
        assert lead.telefone.digits == "91999999999"
        assert lead.captured_url == "https://celogos.com.br/contato"

    def test_salva_lead_no_repo(self, use_case: IngestLeadsterWebhook) -> None:
        repo: FakeLeadRepository = use_case._repo  # type: ignore
        payload = {
            "name": "Maria",
            "email": "maria@test.com",
            "phone": "(11) 11111-1111",
            "url": "https://celogos.com.br/",
        }
        use_case.execute(payload)
        assert len(repo.saved_leads) == 1
        assert repo.saved_leads[0].nome == "Maria"

    def test_envia_identify_para_cdp(self, use_case: IngestLeadsterWebhook) -> None:
        cdp: FakeCDP = use_case._cdp  # type: ignore
        payload = {
            "name": "Ana",
            "email": "ana@test.com",
            "phone": "(21) 22222-2222",
            "url": "https://celogos.com.br/",
        }
        use_case.execute(payload)
        assert len(cdp.identify_calls) == 1
        call = cdp.identify_calls[0]
        assert call["user_id"] == "ana@test.com"
        traits = call["traits"]
        assert traits.get("name") == "Ana"
        assert traits.get("email") == "ana@test.com"

    def test_envia_track_lead_para_cdp(self, use_case: IngestLeadsterWebhook) -> None:
        cdp: FakeCDP = use_case._cdp  # type: ignore
        payload = {
            "name": "Carlos",
            "email": "carlos@test.com",
            "phone": "(31) 33333-3333",
            "url": "https://celogos.com.br/",
        }
        use_case.execute(payload)
        assert len(cdp.track_calls) == 1
        call = cdp.track_calls[0]
        assert call["event"] == "Lead"
        props = call["properties"]
        assert props is not None
        assert props.get("name") == "Carlos"
        assert props.get("email") == "carlos@test.com"

    def test_extrai_tracking_params_do_payload(self, use_case: IngestLeadsterWebhook) -> None:
        payload = {
            "name": "Pedro",
            "email": "pedro@test.com",
            "phone": "(41) 44444-4444",
            "url": "https://celogos.com.br/?utm_source=google&utm_medium=cpc&gclid=XYZ",
            "utm_source": "google",
            "utm_medium": "cpc",
        }
        result = use_case.execute(payload)
        assert result.is_ok()
        assert result.value is not None
        assert result.value.tracking.utm_source == "google"
        assert result.value.tracking.utm_medium == "cpc"

    def test_corrige_typo_utm_campaing(self, use_case: IngestLeadsterWebhook) -> None:
        payload = {
            "name": "Test",
            "email": "test@typo.com",
            "phone": "(51) 55555-5555",
            "url": "https://site.com",
            "utm_campaing": "campanha-errada",
        }
        result = use_case.execute(payload)
        assert result.is_ok()
        assert result.value is not None
        assert result.value.tracking.utm_campaign == "campanha-errada"

    def test_usa_anonymous_id_do_contexto(self, use_case: IngestLeadsterWebhook) -> None:
        cdp: FakeCDP = use_case._cdp  # type: ignore
        payload = {
            "name": "Lucas",
            "email": "lucas@anon.com",
            "phone": "(61) 66666-6666",
            "url": "https://site.com/?segment_anonymous_id=anon-123",
        }
        use_case.execute(payload)
        # identify deve ter anonymousId no context
        identify_call = cdp.identify_calls[0]
        ctx = identify_call.get("context") or {}
        assert ctx.get("anonymousId") == "anon-123"

    def test_inclui_message_id_para_idempotencia(self, use_case: IngestLeadsterWebhook) -> None:
        cdp: FakeCDP = use_case._cdp  # type: ignore
        payload = {
            "name": "Idem",
            "email": "idem@test.com",
            "phone": "(71) 77777-7777",
            "url": "https://site.com",
        }
        use_case.execute(payload)
        track_call = cdp.track_calls[0]
        assert track_call.get("message_id") == "msg-001"

    def test_rejeita_webhook_com_assinatura_invalida(self) -> None:
        strict = IngestLeadsterWebhook(
            repo=FakeLeadRepository(),
            cdp=FakeCDP(),
            clock=FakeClock(),
            id_gen=FakeIdGenerator(),
            geo=FakeGeoIP(),
            verifier=FakeWebhookVerifier(approved=False),
            hmac_secret="secret",
        )
        payload = {
            "name": "Hacker",
            "email": "hacker@evil.com",
            "phone": "(81) 88888-8888",
            "url": "https://site.com",
        }
        body = b'{"name":"Hacker","email":"hacker@evil.com"}'
        result = strict.execute(payload, signature="invalid-sig", body_bytes=body)
        assert result.is_error()
        assert "assinatura" in result.error.lower()

    def test_aceita_lead_com_assinatura_valida(self) -> None:
        strict = IngestLeadsterWebhook(
            repo=FakeLeadRepository(),
            cdp=FakeCDP(),
            clock=FakeClock(),
            id_gen=FakeIdGenerator(),
            geo=FakeGeoIP(),
            verifier=FakeWebhookVerifier(approved=True),
            hmac_secret="secret",
        )
        payload = {
            "name": "Joao",
            "email": "joao@valid.com",
            "phone": "(91) 99999-9999",
            "url": "https://site.com",
        }
        body = b'{"name":"Joao","email":"joao@valid.com"}'
        result = strict.execute(payload, signature="valid-sig", body_bytes=body)
        assert result.is_ok()

    def test_enriquece_com_geoip_quando_ip_fornecido(self, use_case: IngestLeadsterWebhook) -> None:
        payload = {
            "name": "Geo",
            "email": "geo@test.com",
            "phone": "(91) 99999-9999",
            "url": "https://site.com",
            "ip_lead": "8.8.8.8",
        }
        result = use_case.execute(payload)
        assert result.is_ok()
        assert result.value is not None
        assert result.value.location.city == "Belem"  # valor do fake
        assert result.value.location.region == "PA"

    def test_track_envia_location_no_properties(self, use_case: IngestLeadsterWebhook) -> None:
        cdp: FakeCDP = use_case._cdp  # type: ignore
        payload = {
            "name": "Loc",
            "email": "loc@test.com",
            "phone": "(91) 99999-9999",
            "url": "https://site.com",
            "ip_lead": "8.8.8.8",
        }
        use_case.execute(payload)
        props = cdp.track_calls[0]["properties"]
        assert props is not None
        loc = props.get("location")
        assert loc is not None
        assert isinstance(loc, dict)
        assert loc.get("city") == "Belem"
