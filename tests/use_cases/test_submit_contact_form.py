"""Testes para o use case submit_contact_form."""

from __future__ import annotations

import pytest

from src.adapters.fakes import FakeCDP, FakeClock, FakeLeadRepository
from src.use_cases.submit_contact_form import SubmitContactForm


class TestSubmitContactForm:
    @pytest.fixture
    def use_case(self) -> SubmitContactForm:
        return SubmitContactForm(
            repo=FakeLeadRepository(),
            cdp=FakeCDP(),
            clock=FakeClock(),
        )

    def test_submit_valido(self, use_case: SubmitContactForm) -> None:
        result = use_case.execute(
            nome="Joao",
            email="joao@test.com",
            telefone="(91) 99999-9999",
            consentimento=True,
        )
        assert result.is_ok(), f"Esperado sucesso: {result.error}"
        lead = result.value
        assert lead.nome == "Joao"
        assert lead.email.value == "joao@test.com"
        assert lead.telefone is not None
        assert lead.telefone.digits == "91999999999"

    def test_salva_no_repo(self, use_case: SubmitContactForm) -> None:
        repo: FakeLeadRepository = use_case._repo  # type: ignore
        use_case.execute(
            nome="Maria",
            email="maria@test.com",
            telefone="(11) 11111-1111",
            consentimento=True,
        )
        assert len(repo.saved_leads) == 1

    def test_rejeita_nome_vazio(self, use_case: SubmitContactForm) -> None:
        result = use_case.execute(
            nome="", email="a@b.com", telefone="(91) 99999-9999", consentimento=True
        )
        assert result.is_error()

    def test_rejeita_email_vazio(self, use_case: SubmitContactForm) -> None:
        result = use_case.execute(
            nome="Joao", email="", telefone="(91) 99999-9999", consentimento=True
        )
        assert result.is_error()

    def test_rejeita_email_invalido(self, use_case: SubmitContactForm) -> None:
        result = use_case.execute(
            nome="Joao",
            email="invalido",
            telefone="(91) 99999-9999",
            consentimento=True,
        )
        assert result.is_error()

    def test_aceita_sem_telefone(self, use_case: SubmitContactForm) -> None:
        result = use_case.execute(
            nome="Joao",
            email="joao@test.com",
            telefone="",
            consentimento=True,
        )
        assert result.is_ok()
        assert result.value is not None
        assert result.value.telefone is None

    def test_ip_url_e_tracking_sao_opcionais(self, use_case: SubmitContactForm) -> None:
        result = use_case.execute(
            nome="Joao",
            email="joao@test.com",
            telefone="(91) 99999-9999",
            consentimento=False,
            ip="192.168.1.1",
            captured_url="https://site.com",
            tracking_params={"utm_source": "google"},
        )
        assert result.is_ok()
        lead = result.value
        assert lead.ip_lead == "192.168.1.1"
        assert lead.tracking.utm_source == "google"
        assert not lead.consentimento_analytics
