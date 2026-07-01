import json
from pathlib import Path

from django.conf import settings
from django.test import TestCase

from seo.management.commands.seo_minify import ASSETS, min_path


class MinifiedAssetsTest(TestCase):
    """Os fontes hand-written devem ter .min versionado, menor, e referenciado nos partials."""

    def _static(self, rel):
        return Path(settings.BASE_DIR) / "static" / rel

    def test_min_files_exist_and_are_smaller(self):
        for rel in ASSETS:
            src = self._static(rel)
            dst = self._static(min_path(rel))
            self.assertTrue(dst.exists(), f"faltando {min_path(rel)} (rode seo_minify)")
            self.assertLess(
                dst.stat().st_size,
                src.stat().st_size,
                f"{dst.name} não é menor que a fonte",
            )

    def test_partials_reference_the_min_variants(self):
        partials = Path(settings.BASE_DIR) / "templates" / "partials"
        blob = (partials / "head.html").read_text(encoding="utf-8") + (
            partials / "script.html"
        ).read_text(encoding="utf-8")
        for rel in ASSETS:
            self.assertIn(min_path(rel), blob, f"partial não referencia {min_path(rel)}")
            # não deve sobrar referência ao fonte não-minificado
            self.assertNotIn(f"'{rel}'", blob, f"ainda referencia o fonte {rel}")


class WebManifestTest(TestCase):
    """O manifest deve existir, ser JSON válido e ser servido (antes retornava 404)."""

    def test_manifest_file_is_valid(self):
        path = Path(settings.BASE_DIR) / "static" / "manifest.webmanifest"
        self.assertTrue(path.exists(), "manifest.webmanifest ausente em static/")
        data = json.loads(path.read_text(encoding="utf-8"))
        for key in ("name", "start_url", "display", "icons"):
            self.assertIn(key, data, f"manifest sem chave obrigatória: {key}")
        self.assertTrue(data["icons"], "manifest sem ícones")

    def test_head_references_manifest_via_static(self):
        head = (
            Path(settings.BASE_DIR) / "templates" / "partials" / "head.html"
        ).read_text(encoding="utf-8")
        self.assertIn("{% static 'manifest.webmanifest' %}", head)
        self.assertNotIn('href="/static/manifest.webmanifest"', head)
