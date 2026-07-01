import re
from pathlib import Path

from django.conf import settings
from django.test import TestCase

# Captura src e alt de cada <img> (ordem src antes de alt nos templates atuais).
IMG_RE = re.compile(r'<img\s+src="([^"]+)"[^>]*?\balt="([^"]*)"', re.DOTALL)

SERVICE_TEMPLATES = [
    "servico_infantil.html",
    "servico_fundamental1.html",
    "servico_fundamental2.html",
    "servico_medio.html",
    "servico_integral.html",
]


class ServiceImagesAltTest(TestCase):
    """Imagens de conteúdo (não decorativas) nos serviços devem ter alt não-vazio.

    Imagens decorativas ficam sob ``/shape/`` e mantêm ``alt=""`` de propósito
    (leitores de tela as ignoram). As demais são conteúdo e precisam de alt para SEO.
    """

    def test_content_images_have_non_empty_alt(self):
        base = Path(settings.BASE_DIR) / "templates" / "services"
        missing = []
        for name in SERVICE_TEMPLATES:
            html = (base / name).read_text(encoding="utf-8")
            for src, alt in IMG_RE.findall(html):
                if "/shape/" in src:
                    continue  # decorativa: alt vazio é correto
                if not alt.strip():
                    missing.append(f"{name}: {src}")
        self.assertEqual(missing, [], f"imagens de conteúdo sem alt: {missing}")
