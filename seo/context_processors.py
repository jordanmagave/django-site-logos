# seo/context_processors.py
from django.conf import settings

from .metadata import get_metadata


def seo_context(request):
    """Injeta title/description/canonical/og por página em todos os templates."""
    resolver_match = getattr(request, "resolver_match", None)
    url_name = getattr(resolver_match, "url_name", None)
    meta = get_metadata(url_name)

    host = settings.CANONICAL_HOST
    canonical_url = f"https://{host}{request.path}"
    og_image = f"https://{host}/static/images/logo/logo-1.svg"

    return {
        "seo_title": meta["title"],
        "seo_description": meta["description"],
        "seo_og_title": meta.get("og_title", meta["title"]),
        "seo_og_description": meta.get("og_description", meta["description"]),
        "seo_og_image": og_image,
        "canonical_url": canonical_url,
    }
