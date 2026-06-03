"""Testes RED para value objects do domínio leads."""

from __future__ import annotations

import pytest

from src.domain.errors import InvalidEmailError, InvalidPhoneError
from src.domain.leads.value_objects import (
    AnonymousId,
    Email,
    MessageId,
    Phone,
    TrackingParams,
)


class TestEmail:
    def test_aceita_email_valido(self) -> None:
        email = Email("user@example.com")
        assert email.value == "user@example.com"

    def test_normaliza_para_lowercase(self) -> None:
        email = Email("User@Example.COM")
        assert email.value == "user@example.com"

    def test_remove_espacos_externos(self) -> None:
        email = Email("  user@example.com  ")
        assert email.value == "user@example.com"

    @pytest.mark.parametrize(
        "invalido",
        ["", "sem-arroba", "@example.com", "user@", "user@example", "user @ example.com"],
    )
    def test_rejeita_email_invalido(self, invalido: str) -> None:
        with pytest.raises(InvalidEmailError):
            Email(invalido)

    def test_igualdade_por_valor(self) -> None:
        assert Email("a@b.com") == Email("A@B.COM")
        assert hash(Email("a@b.com")) == hash(Email("A@B.COM"))

    def test_imutavel(self) -> None:
        email = Email("a@b.com")
        with pytest.raises((AttributeError, TypeError)):
            email.value = "outro@b.com"  # type: ignore[misc]


class TestPhone:
    def test_aceita_formato_brasileiro_padrao(self) -> None:
        phone = Phone("(91) 99999-9999")
        assert phone.digits == "91999999999"

    def test_normaliza_removendo_caracteres_nao_digitos(self) -> None:
        phone = Phone("+55 91 9 9999-9999")
        assert phone.digits == "5591999999999"

    def test_preserva_apenas_digitos(self) -> None:
        phone = Phone("(11) 11111-1111")
        assert phone.digits == "11111111111"

    @pytest.mark.parametrize("invalido", ["", "abc", "12", "123", "0"])
    def test_rejeita_telefone_curto_demais(self, invalido: str) -> None:
        with pytest.raises(InvalidPhoneError):
            Phone(invalido)

    def test_igualdade_por_digitos(self) -> None:
        assert Phone("(91) 99999-9999") == Phone("91 9 9999 9999")


class TestTrackingParams:
    def test_extrai_utms_de_dict(self) -> None:
        raw = {
            "utm_source": "google",
            "utm_medium": "cpc",
            "utm_campaign": "verao",
            "gclid": "XYZ",
            "fbclid": "ABC",
            "outro": "ignorado",
        }
        tp = TrackingParams.from_mapping(raw)
        assert tp.utm_source == "google"
        assert tp.utm_medium == "cpc"
        assert tp.utm_campaign == "verao"
        assert tp.gclid == "XYZ"
        assert tp.fbclid == "ABC"

    def test_corrige_typo_utm_campaing(self) -> None:
        """Bug critico do payload Leadster: vem 'utm_campaing' (typo)."""
        raw = {"utm_campaing": "campanha-typo"}
        tp = TrackingParams.from_mapping(raw)
        assert tp.utm_campaign == "campanha-typo"

    def test_utm_campaign_correto_tem_prioridade_sobre_typo(self) -> None:
        raw = {"utm_campaign": "correto", "utm_campaing": "typo"}
        tp = TrackingParams.from_mapping(raw)
        assert tp.utm_campaign == "correto"

    def test_campos_ausentes_ficam_none(self) -> None:
        tp = TrackingParams.from_mapping({})
        assert tp.utm_source is None
        assert tp.utm_medium is None
        assert tp.utm_campaign is None
        assert tp.gclid is None
        assert tp.fbclid is None

    def test_from_url_extrai_query_string(self) -> None:
        url = (
            "https://site.com/page?utm_source=fb&utm_medium=cpc&"
            "gclid=XYZ&fbclid=ABC&segment_anonymous_id=anon-123"
        )
        tp = TrackingParams.from_url(url)
        assert tp.utm_source == "fb"
        assert tp.gclid == "XYZ"
        assert tp.fbclid == "ABC"
        assert tp.anonymous_id == "anon-123"

    def test_from_url_sem_query(self) -> None:
        tp = TrackingParams.from_url("https://site.com/page")
        assert tp.utm_source is None
        assert tp.gclid is None

    def test_fbc_gerado_a_partir_de_fbclid_se_ausente(self) -> None:
        tp = TrackingParams.from_url(
            "https://site.com/p?fbclid=abc123",
            now_ms=1700000000000,
        )
        assert tp.fbclid == "abc123"
        assert tp.fbc is not None
        assert tp.fbc.startswith("fb.")
        assert "1700000000000" in tp.fbc
        assert tp.fbc.endswith("abc123")

    def test_fbc_respeita_subdomain_www(self) -> None:
        tp = TrackingParams.from_url(
            "https://www.site.com/p?fbclid=abc",
            now_ms=1000,
        )
        # subdomain index 2 para www.*
        assert tp.fbc == "fb.2.1000.abc"

    def test_fbc_sem_www_subdomain_1(self) -> None:
        tp = TrackingParams.from_url(
            "https://site.com/p?fbclid=abc",
            now_ms=1000,
        )
        assert tp.fbc == "fb.1.1000.abc"

    def test_fbc_existente_nao_e_sobrescrito(self) -> None:
        tp = TrackingParams.from_url(
            "https://site.com/p?fbclid=novo&fbc=fb.1.999.original",
            now_ms=1000,
        )
        assert tp.fbc == "fb.1.999.original"


class TestAnonymousId:
    def test_aceita_id_nao_vazio(self) -> None:
        aid = AnonymousId("anon-abc-123")
        assert aid.value == "anon-abc-123"

    def test_rejeita_vazio(self) -> None:
        with pytest.raises(ValueError):
            AnonymousId("")

    def test_igualdade_por_valor(self) -> None:
        assert AnonymousId("x") == AnonymousId("x")


class TestMessageId:
    def test_gerado_e_estavel_para_mesma_entrada(self) -> None:
        """Idempotencia: mesmo email + janela de tempo -> mesmo messageId."""
        m1 = MessageId.for_lead(email="user@example.com", window_ms=1_700_000_000_000)
        m2 = MessageId.for_lead(email="user@example.com", window_ms=1_700_000_000_000)
        assert m1 == m2

    def test_emails_diferentes_geram_ids_diferentes(self) -> None:
        m1 = MessageId.for_lead(email="a@b.com", window_ms=1_700_000_000_000)
        m2 = MessageId.for_lead(email="b@c.com", window_ms=1_700_000_000_000)
        assert m1 != m2

    def test_janelas_diferentes_geram_ids_diferentes(self) -> None:
        m1 = MessageId.for_lead(email="a@b.com", window_ms=1_700_000_000_000)
        m2 = MessageId.for_lead(email="a@b.com", window_ms=1_700_000_001_000)
        assert m1 != m2

    def test_email_normalizado_antes_de_hash(self) -> None:
        m1 = MessageId.for_lead(email="USER@example.com", window_ms=1000)
        m2 = MessageId.for_lead(email="user@example.com", window_ms=1000)
        assert m1 == m2

    def test_formato_e_string_nao_vazia(self) -> None:
        m = MessageId.for_lead(email="a@b.com", window_ms=1000)
        assert isinstance(m.value, str)
        assert len(m.value) > 16
