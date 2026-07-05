"""Testes das peças de SEO portadas para a arquitetura atual da main.

Cobre: host canônico sem-www (301 www→raiz), llms.txt e o baseline de audit
(AuditFinding + comando seo_import_semrush).
"""

import csv
import tempfile
from pathlib import Path

from django.core.management import call_command
from django.test import TestCase, override_settings


@override_settings(ALLOWED_HOSTS=["celogos.com.br", "www.celogos.com.br", "testserver"])
class CanonicalHostTest(TestCase):
    def test_www_faz_301_para_raiz(self):
        resp = self.client.get("/about/", HTTP_HOST="www.celogos.com.br")
        self.assertEqual(resp.status_code, 301)
        self.assertEqual(resp["Location"], "https://celogos.com.br/about/")

    def test_www_preserva_querystring(self):
        resp = self.client.get("/?utm_source=x", HTTP_HOST="www.celogos.com.br")
        self.assertEqual(resp.status_code, 301)
        self.assertEqual(resp["Location"], "https://celogos.com.br/?utm_source=x")

    def test_raiz_sem_www_nao_redireciona(self):
        resp = self.client.get("/", HTTP_HOST="celogos.com.br")
        self.assertEqual(resp.status_code, 200)

    def test_canonical_e_paginas_sem_www(self):
        resp = self.client.get("/about/", HTTP_HOST="celogos.com.br")
        html = resp.content.decode("utf-8")
        self.assertIn('rel="canonical"', html)
        self.assertNotIn("https://www.celogos.com.br", html)


@override_settings(ALLOWED_HOSTS=["celogos.com.br", "testserver"])
class SitemapRobotsHostTest(TestCase):
    def test_sitemap_usa_host_sem_www(self):
        resp = self.client.get("/sitemap.xml", HTTP_HOST="celogos.com.br")
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode("utf-8")
        self.assertIn("https://celogos.com.br", body)
        self.assertNotIn("www.celogos.com.br", body)

    def test_robots_aponta_sitemap_sem_www(self):
        resp = self.client.get("/robots.txt", HTTP_HOST="celogos.com.br")
        self.assertEqual(resp.status_code, 200)
        body = resp.content.decode("utf-8")
        self.assertIn("Sitemap:", body)
        self.assertNotIn("www.celogos.com.br", body)


class LlmsTxtTest(TestCase):
    def test_llms_txt_ok(self):
        resp = self.client.get("/llms.txt")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/plain", resp["Content-Type"])
        body = resp.content.decode("utf-8")
        self.assertIn("Centro Educacional Logos", body)


class SeoImportSemrushTest(TestCase):
    def _csv(self, rows):
        f = tempfile.NamedTemporaryFile(
            mode="w", suffix="_20260701.csv", delete=False, encoding="utf-8-sig", newline=""
        )
        w = csv.writer(f)
        w.writerow(["Page URL", "Issue A", "Issue B"])
        for r in rows:
            w.writerow(r)
        f.close()
        return f.name

    def test_importa_cria_findings_idempotente(self):
        from fluxi.models import AuditFinding

        path = self._csv(
            [
                ["https://celogos.com.br/", "3", "0"],
                ["https://celogos.com.br/about/", "0", "5"],
            ]
        )
        call_command("seo_import_semrush", path)
        # 3 findings com count>0 (raiz/IssueA, about/IssueB) — zeros são ignorados
        self.assertEqual(AuditFinding.objects.count(), 2)
        self.assertEqual(
            AuditFinding.objects.get(page_url="https://celogos.com.br/", issue="Issue A").count,
            3,
        )
        # reimportar a mesma data não duplica
        call_command("seo_import_semrush", path)
        self.assertEqual(AuditFinding.objects.count(), 2)
        Path(path).unlink(missing_ok=True)
