# seo/management/commands/seo_minify.py
"""Gera versões ``.min`` dos CSS/JS hand-written que o Semrush marca como não-minificados.

Usa minificadores **conservadores** (``rcssmin``/``rjsmin``): removem apenas espaço em
branco e comentários, sem renomear identificadores — risco baixo de quebrar comportamento.
Os arquivos vendor já-minificados (bootstrap, swiper, gsap, jqueryui...) ficam **de fora**
de propósito. Os ``.min`` gerados são versionados no repo; rode este comando e recommite
sempre que editar um dos fontes abaixo. Ver [[seo-on-page]].

Requer (dev/build): ``pip install rcssmin rjsmin``.
"""

from pathlib import Path, PurePosixPath

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

# Fontes hand-written (não-minificados) referenciados nos partials.
ASSETS = [
    "css/style.css",
    "css/custom.css",
    "css/plugins/magnific-popup.css",
    "css/plugins/metismenu.css",
    "js/main.js",
    "js/plugins/metismenu.js",
]


def min_path(rel):
    """``css/style.css`` -> ``css/style.min.css``; ``js/main.js`` -> ``js/main.min.js``.

    Usa POSIX (``/``) sempre — é caminho de URL estática, não do filesystem do SO.
    """
    p = PurePosixPath(rel)
    return f"{p.with_suffix('')}.min{p.suffix}"


class Command(BaseCommand):
    help = "Gera .min de CSS/JS hand-written (rcssmin/rjsmin conservadores)."

    def handle(self, *args, **options):
        try:
            import rcssmin
            import rjsmin
        except ImportError as exc:  # pragma: no cover - erro de ambiente
            raise CommandError(
                "Faltam os minificadores. Rode: pip install rcssmin rjsmin"
            ) from exc

        static_dir = Path(settings.BASE_DIR) / "static"
        for rel in ASSETS:
            src = static_dir / rel
            if not src.exists():
                raise CommandError(f"Fonte não encontrada: {rel}")
            text = src.read_text(encoding="utf-8")
            if rel.endswith(".css"):
                out = rcssmin.cssmin(text)
            else:
                out = rjsmin.jsmin(text)
            dst = static_dir / min_path(rel)
            dst.write_text(out, encoding="utf-8")
            pct = 100 * (1 - len(out) / len(text)) if text else 0
            self.stdout.write(
                f"{rel}: {len(text):>7}B -> {dst.name} {len(out):>7}B  (-{pct:.0f}%)"
            )
        self.stdout.write(self.style.SUCCESS("Minificação concluída."))
