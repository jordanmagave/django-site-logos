"""Testes da Fase 1 de SEO (correções técnicas do baseline Semrush).

Cobre: compressão de HTML (GZip), HSTS + redirect https, metadados sociais
(OG/Twitter/canonical) por página, e canônico dos serviços alinhado à rota real.
"""

from django.test import TestCase, override_settings

SERVICE_PATHS = [
    "/servicos-educacionais/educacao-infantil",
    "/servicos-educacionais/ensino-fundamental-1",
    "/servicos-educacionais/ensino-fundamental-2",
    "/servicos-educacionais/ensino-medio",
    "/servicos-educacionais/integral",
]


@override_settings(ALLOWED_HOSTS=["celogos.com.br", "testserver"])
class GzipCompressionTest(TestCase):
    def test_home_responde_gzip_quando_aceito(self):
        resp = self.client.get("/", HTTP_ACCEPT_ENCODING="gzip", HTTP_HOST="celogos.com.br")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get("Content-Encoding"), "gzip")

    def test_home_nao_comprime_sem_accept_encoding(self):
        resp = self.client.get("/", HTTP_ACCEPT_ENCODING="", HTTP_HOST="celogos.com.br")
        self.assertEqual(resp.status_code, 200)
        self.assertIsNone(resp.get("Content-Encoding"))


@override_settings(ALLOWED_HOSTS=["celogos.com.br", "testserver"])
class SecurityHeadersTest(TestCase):
    @override_settings(SECURE_HSTS_SECONDS=31536000, SECURE_HSTS_INCLUDE_SUBDOMAINS=True)
    def test_hsts_presente_em_request_https(self):
        resp = self.client.get("/", secure=True, HTTP_HOST="celogos.com.br")
        self.assertIn("Strict-Transport-Security", resp)
        self.assertIn("max-age=31536000", resp["Strict-Transport-Security"])

    @override_settings(SECURE_SSL_REDIRECT=True)
    def test_http_redireciona_para_https(self):
        resp = self.client.get("/", HTTP_HOST="celogos.com.br")
        self.assertEqual(resp.status_code, 301)
        self.assertTrue(resp["Location"].startswith("https://celogos.com.br"))


@override_settings(ALLOWED_HOSTS=["celogos.com.br", "testserver"])
class SocialMetadataTest(TestCase):
    def test_pagina_servico_tem_og_especifico(self):
        resp = self.client.get("/servicos-educacionais/ensino-medio", HTTP_HOST="celogos.com.br")
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode("utf-8")
        self.assertIn('property="og:title"', html)
        self.assertIn("Ensino Médio", html)
        # og:url deve apontar para a canônica da página, não para a home
        self.assertIn(
            'property="og:url" content="https://celogos.com.br/servicos-educacionais/ensino-medio"',
            html,
        )

    def test_home_mantem_og_padrao(self):
        resp = self.client.get("/", HTTP_HOST="celogos.com.br")
        html = resp.content.decode("utf-8")
        self.assertIn('property="og:url" content="https://celogos.com.br"', html)


@override_settings(ALLOWED_HOSTS=["celogos.com.br", "testserver"])
class ServiceCanonicalTest(TestCase):
    def test_canonical_de_cada_servico_resolve_200(self):
        for path in SERVICE_PATHS:
            with self.subTest(path=path):
                resp = self.client.get(path, HTTP_HOST="celogos.com.br")
                self.assertEqual(resp.status_code, 200)
                html = resp.content.decode("utf-8")
                canonical = f'<link rel="canonical" href="https://celogos.com.br{path}"'
                self.assertIn(canonical, html)
