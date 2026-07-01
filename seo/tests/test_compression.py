from django.test import TestCase, override_settings


@override_settings(ALLOWED_HOSTS=["testserver"])
class GzipTest(TestCase):
    def test_html_response_is_gzipped_when_accepted(self):
        # GZipMiddleware só comprime respostas acima de 200 bytes; a home é grande.
        resp = self.client.get("/", HTTP_ACCEPT_ENCODING="gzip, deflate")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get("Content-Encoding"), "gzip")


class NoDeprecatedPolyfillTest(TestCase):
    """polyfill.io foi depreciado/sinkholed e retornava 403 — não deve mais existir."""

    def test_polyfill_removed_from_templates(self):
        from pathlib import Path
        from django.conf import settings

        templates_dir = Path(settings.BASE_DIR) / "templates"
        offenders = [
            str(p)
            for p in templates_dir.rglob("*.html")
            if "polyfill" in p.read_text(encoding="utf-8").lower()
        ]
        self.assertEqual(offenders, [], f"referência a polyfill em: {offenders}")
