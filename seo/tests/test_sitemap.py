from django.test import TestCase, override_settings


@override_settings(ALLOWED_HOSTS=["testserver", "celogos.com.br"])
class SitemapRobotsLlmsTest(TestCase):
    def test_sitemap_ok_and_lists_pages_non_www(self):
        resp = self.client.get("/sitemap.xml")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("application/xml", resp["Content-Type"])
        body = resp.content.decode("utf-8")
        # host canônico e https, nunca www
        self.assertIn("https://celogos.com.br/", body)
        self.assertNotIn("https://www.celogos.com.br", body)
        self.assertNotIn("example.com", body)
        # inclui páginas principais
        for path in ["/about/", "/contato/", "/servicos-educacionais/ensino-medio"]:
            self.assertIn(f"https://celogos.com.br{path}", body)
        # nunca lista o slug legado com underscore
        self.assertNotIn("contato_logos", body)

    def test_robots_ok_text_plain_with_sitemap(self):
        resp = self.client.get("/robots.txt")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "text/plain")
        body = resp.content.decode("utf-8")
        self.assertIn("User-agent: *", body)
        self.assertIn("Sitemap: https://celogos.com.br/sitemap.xml", body)

    def test_llms_ok_text_plain(self):
        resp = self.client.get("/llms.txt")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp["Content-Type"], "text/plain")
        self.assertIn("Centro Educacional Logos", resp.content.decode("utf-8"))
