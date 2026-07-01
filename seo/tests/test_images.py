import re
from pathlib import Path

from django.conf import settings
from django.test import TestCase


class AboutImagesExistTest(TestCase):
    """Todas as imagens estáticas referenciadas em about.html devem existir em disco."""

    def test_about_static_images_exist(self):
        template = Path(settings.BASE_DIR) / "templates" / "pages" / "about.html"
        html = template.read_text(encoding="utf-8")
        refs = re.findall(r'src="(/static/[^"]+)"', html)
        missing = []
        for ref in refs:
            rel = ref.replace("/static/", "", 1)
            if not (Path(settings.BASE_DIR) / "static" / rel).exists():
                missing.append(ref)
        self.assertEqual(missing, [], f"imagens quebradas em about.html: {missing}")
