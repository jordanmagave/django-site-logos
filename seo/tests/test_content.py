import re
from pathlib import Path

from django.conf import settings
from django.test import TestCase


TAG_RE = re.compile(r"<[^>]+>")
DJ_RE = re.compile(r"\{%.*?%\}|\{\{.*?\}\}", re.DOTALL)


def _visible_words(template_relpath):
    """Palavras visíveis do próprio template (sem tags HTML nem sintaxe Django)."""
    path = Path(settings.BASE_DIR) / "templates" / template_relpath
    text = path.read_text(encoding="utf-8")
    text = DJ_RE.sub(" ", text)
    text = TAG_RE.sub(" ", text)
    return [w for w in re.split(r"\s+", text) if w.strip()]


class ThinContentTest(TestCase):
    """Páginas antes marcadas como 'low word count' devem ter conteúdo próprio suficiente."""

    def test_contato_has_enough_content(self):
        words = _visible_words("pages/contato.html")
        self.assertGreaterEqual(
            len(words), 120, f"/contato/ ainda com pouco conteúdo ({len(words)} palavras)"
        )

    def test_integral_has_enough_content(self):
        words = _visible_words("services/servico_integral.html")
        self.assertGreaterEqual(
            len(words), 220, f"/integral ainda com pouco conteúdo ({len(words)} palavras)"
        )

    def test_contato_shows_real_nap(self):
        text = " ".join(_visible_words("pages/contato.html"))
        self.assertIn("Passagem Miranda", text)
        self.assertIn("Coqueiro", text)
        self.assertIn("3013-0198", text)
