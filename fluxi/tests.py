# fluxi/tests.py

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse
from .models import Contato
from unittest.mock import patch


class ContatoModelTest(TestCase):
    def test_criar_contato(self):
        """Verifica se um objeto Contato pode ser criado com sucesso."""
        contato = Contato.objects.create(
            nome="Usuario Teste",
            email="teste@exemplo.com",
            telefone="(99) 99999-9999",
            gclid="teste-gclid-123",
        )
        self.assertEqual(contato.nome, "Usuario Teste")
        self.assertEqual(contato.gclid, "teste-gclid-123")
        self.assertEqual(str(contato), "Usuario Teste - (99) 99999-9999")

    def test_telefone_invalido_lanca_erro(self):
        """Verifica se a criação de um Contato com telefone inválido levanta um ValidationError."""
        with self.assertRaises(ValidationError):
            contato = Contato(
                nome="Telefone Invalido",
                email="valido@exemplo.com",
                telefone="12345",  # Formato inválido
            )
            contato.full_clean()


class ContatoViewTest(TestCase):
    def test_pagina_de_contato_carrega_corretamente(self):
        """Verifica se a página de contato (GET) carrega com sucesso."""
        response = self.client.get(reverse("contato"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/contato.html")

    def test_envio_de_formulario_com_sucesso(self):
        """Verifica se o envio do formulário (POST) cria um contato."""
        form_data = {
            "nome": "Novo Contato",
            "email": "novo@exemplo.com",
            "telefone": "(11) 11111-1111",
        }

        response = self.client.post(reverse("contato"), data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Contato.objects.filter(email="novo@exemplo.com").exists())

    def test_envio_de_formulario_invalido(self):
        """Verifica se o envio de um formulário inválido não cria um contato."""
        form_data = {
            "nome": "Contato Invalido",
            "email": "email-invalido",  # E-mail sem @
            "telefone": "(33) 33333-3333",
        }

        response = self.client.post(reverse("contato"), data=form_data)

        # 1. Verifica se a página recarregou com sucesso (não redirecionou)
        self.assertEqual(response.status_code, 200)

        # 2. Verifica se NENHUM contato foi criado no banco
        self.assertFalse(Contato.objects.filter(nome="Contato Invalido").exists())


class MiddlewareBehaviorTest(TestCase):
    def test_parametros_sao_salvos_na_sessao(self):
        """Verifica se os parâmetros de rastreamento da URL são salvos na sessão."""
        # Cria a URL com os parâmetros de teste
        url = reverse("contato") + "?utm_source=google&gclid=teste123"

        # Simula a visita a essa URL
        self.client.get(url)

        # Verifica se os valores foram salvos corretamente na sessão do cliente de teste
        self.assertEqual(self.client.session["utm_source"], "google")
        self.assertEqual(self.client.session["gclid"], "teste123")


class StaticFilesTest(TestCase):
    def test_arquivos_estaticos_sao_carregados(self):
        """Verifica se os arquivos estáticos são carregados corretamente."""
        response = self.client.get(reverse("contato"))
        self.assertContains(response, "style.css")
        self.assertContains(response, "css-purged")


class SecurityHeadersTest(TestCase):
    def test_cabecalhos_de_seguranca_estao_presentes(self):
        """Verifica se os cabeçalhos de segurança estão na resposta da página inicial."""
        response = self.client.get(reverse("contato"))

        # Verifica a presença e o valor dos cabeçalhos
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
