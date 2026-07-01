import re
from pathlib import Path

from django.conf import settings
from django.test import TestCase

# href/src apontando direto para /static/....(js|css) fura o WhiteNoise
# (não recebe hash/immutable nem a variante comprimida). Deve usar {% static %}.
HARDCODED_RE = re.compile(r'(?:src|href)="/static/[^"]+\.(?:js|css)"')

PARTIALS = ["head.html", "script.html"]


class NoHardcodedStaticAssetsTest(TestCase):
    """CSS/JS nos partials devem usar {% static %}, não caminho /static/ fixo."""

    def test_no_hardcoded_js_css_in_partials(self):
        base = Path(settings.BASE_DIR) / "templates" / "partials"
        offenders = {}
        for name in PARTIALS:
            html = (base / name).read_text(encoding="utf-8")
            hits = HARDCODED_RE.findall(html)
            if hits:
                offenders[name] = hits
        self.assertEqual(offenders, {}, f"assets hardcoded em /static/: {offenders}")
