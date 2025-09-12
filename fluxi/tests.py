# fluxi/tests.py

from django.test import TestCase
from django.core.exceptions import ValidationError
from django.urls import reverse
from unittest.mock import patch
from celery.exceptions import Retry
from .models import Contato
from .tasks import send_rudderstack_event


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
            # O erro só é levantado quando validamos o modelo completo
            contato.full_clean()


class ContatoViewTest(TestCase):
    def test_pagina_de_contato_carrega_corretamente(self):
        """Verifica se a página de contato (GET) carrega com sucesso."""
        response = self.client.get(reverse("contato"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "pages/contato.html")

    @patch("fluxi.pagesViews.send_rudderstack_event.delay")
    def test_envio_de_formulario_com_sucesso_e_chama_celery(self, mock_send_event):
        """Verifica se o envio do formulário (POST) cria um contato e chama a tarefa do Celery."""
        form_data = {
            "nome": "Novo Contato",
            "email": "novo@exemplo.com",
            "telefone": "(11) 11111-1111",
        }

        response = self.client.post(reverse("contato"), data=form_data)

        self.assertEqual(response.status_code, 302)
        self.assertTrue(Contato.objects.filter(email="novo@exemplo.com").exists())
        mock_send_event.assert_called_once()

    @patch("fluxi.pagesViews.send_rudderstack_event.delay")
    def test_envio_de_formulario_invalido(self, mock_send_event):
        """Verifica se o envio de um formulário inválido não cria um contato e não chama o Celery."""
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

        # 3. Verifica se a tarefa do Celery NÃO foi chamada
        mock_send_event.assert_not_called()

    @patch("fluxi.pagesViews.send_rudderstack_event.delay")
    def test_parametros_de_rastreamento_sao_salvos_no_contato(self, mock_send_event):
        """
        Simula um usuário visitando com parâmetros UTM e depois enviando o formulário,
        verificando se os parâmetros são salvos no objeto Contato.
        """
        # Passo 1: Simula a visita inicial com parâmetros de rastreamento
        url_com_parametros = (
            reverse("contato") + "?utm_source=facebook&gclid=fb_test_987"
        )
        self.client.get(url_com_parametros)

        # Confirma que os parâmetros foram salvos na sessão
        self.assertEqual(self.client.session["utm_source"], "facebook")
        self.assertEqual(self.client.session["gclid"], "fb_test_987")

        # Passo 2: Simula o envio do formulário na mesma sessão
        form_data = {
            "nome": "Contato de Campanha",
            "email": "campanha@exemplo.com",
            "telefone": "(44) 44444-4444",
        }
        self.client.post(reverse("contato"), data=form_data)

        # Passo 3: Verifica o resultado no banco de dados
        contato_criado = Contato.objects.get(email="campanha@exemplo.com")

        self.assertEqual(contato_criado.nome, "Contato de Campanha")
        self.assertEqual(contato_criado.utm_source, "facebook")
        self.assertEqual(contato_criado.gclid, "fb_test_987")

        # Garante que a tarefa do Celery ainda foi chamada
        mock_send_event.assert_called_once()


class TrackingMiddlewareTest(TestCase):
    def test_parametros_sao_salvos_na_sessao(self):
        """Verifica se os parâmetros de rastreamento da URL são salvos na sessão."""
        # Cria a URL com os parâmetros de teste
        url = reverse("contato") + "?utm_source=google&gclid=teste123"

        # Simula a visita a essa URL
        self.client.get(url)

        # Verifica se os valores foram salvos corretamente na sessão do cliente de teste
        self.assertEqual(self.client.session["utm_source"], "google")
        self.assertEqual(self.client.session["gclid"], "teste123")


class CeleryTaskTest(TestCase):
    @patch("fluxi.tasks.rudderanalytics.track")
    def test_send_rudderstack_event_chama_sdk(self, mock_rudder_track):
        """Verifica se a tarefa do Celery chama o método 'track' do RudderStack."""
        properties = {"email": "task@test.com"}
        anonymous_id = "anon123"

        # Chama a função da tarefa diretamente, como uma função Python normal
        send_rudderstack_event(properties, anonymous_id)

        # Verifica se o método 'track' do SDK foi chamado com os argumentos corretos
        mock_rudder_track.assert_called_once_with(
            anonymous_id=anonymous_id,
            event="Formulario de Contato Enviado",
            properties=properties,
        )


class CeleryTaskFailureTest(TestCase):

    @patch("fluxi.tasks.rudderanalytics.track")
    def test_falha_no_envio_tenta_reenviar(self, mock_rudder_track):
        """
        Verifica se a tarefa do Celery tenta reenviar em caso de falha na API.
        """
        # Configura o mock para simular um erro quando for chamado
        mock_rudder_track.side_effect = Exception("Falha na API do RudderStack")

        properties = {"email": "falha@teste.com"}
        anonymous_id = "anon_falha_123"

        # Usamos um 'try/except' para capturar a exceção 'Retry' que o Celery levanta
        # quando uma tarefa pede para ser reenviada.
        with self.assertRaises(Exception):
            send_rudderstack_event(properties, anonymous_id)

        # Verifica se o método 'track' foi chamado uma vez (a tentativa que falhou)
        mock_rudder_track.assert_called_once()


class SecurityHeadersTest(TestCase):
    def test_cabecalhos_de_seguranca_estao_presentes(self):
        """Verifica se os cabeçalhos de segurança estão na resposta da página inicial."""
        response = self.client.get(reverse("contato"))

        # Verifica a presença e o valor dos cabeçalhos
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
