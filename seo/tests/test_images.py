import os
import re
from pathlib import Path

from django.conf import settings
from django.test import TestCase

STATIC_SRC_RE = re.compile(r'src="/static/([^"]+)"')

# Templates com imagens de conteúdo referenciadas por caminho /static/ fixo.
TEMPLATES = [
    "pages/about.html",
    "pages/contato.html",
    "home/index.html",
    "services/servico_infantil.html",
    "services/servico_fundamental1.html",
    "services/servico_fundamental2.html",
    "services/servico_medio.html",
    "services/servico_integral.html",
]


def _exists_case_sensitive(static_dir, rel):
    """Existe com a MESMA capitalização? (Windows é case-insensitive; Cloud Run/Linux não.)"""
    # tolera espaço/query e normaliza separador
    rel = rel.split("?", 1)[0]
    p = static_dir / Path(rel)
    parent = p.parent
    if not parent.is_dir():
        return False
    return p.name in os.listdir(parent)


class StaticImagesExistTest(TestCase):
    """Imagens referenciadas nos templates devem existir em disco, com case exato.

    Pega imagens quebradas (404) e mismatch de maiúscula/minúscula que só quebra
    no filesystem case-sensitive do Cloud Run.
    """

    def test_referenced_static_images_exist(self):
        static_dir = Path(settings.BASE_DIR) / "static"
        base = Path(settings.BASE_DIR) / "templates"
        missing = []
        for tpl in TEMPLATES:
            html = (base / tpl).read_text(encoding="utf-8")
            for rel in STATIC_SRC_RE.findall(html):
                if not _exists_case_sensitive(static_dir, rel):
                    missing.append(f"{tpl}: /static/{rel}")
        self.assertEqual(missing, [], f"imagens quebradas/case errado: {missing}")
