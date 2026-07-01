# seo/views.py
from django.conf import settings
from django.http import HttpResponse
from django.urls import reverse

from .metadata import get_metadata
from .sitemaps import StaticViewSitemap


def _base_url():
    return f"https://{settings.CANONICAL_HOST}"


def robots_txt(request):
    """robots.txt permitindo tudo (exceto admin) e apontando para o sitemap."""
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "",
        f"Sitemap: {_base_url()}/sitemap.xml",
        "",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def llms_txt(request):
    """llms.txt (llmstxt.org): resumo estruturado do site para LLMs."""
    base = _base_url()
    lines = [
        "# Centro Educacional Logos",
        "",
        "> Escola cristã em Ananindeua (PA) com formação integral da Educação "
        "Infantil ao Ensino Médio.",
        "",
        "## Páginas",
    ]
    for name in StaticViewSitemap.PAGES:
        meta = get_metadata(name)
        url = f"{base}{reverse(name)}"
        lines.append(f"- [{meta['title']}]({url}): {meta['description']}")
    lines.append("")
    return HttpResponse("\n".join(lines), content_type="text/plain")
