# seo/structured_data.py
"""Dados estruturados (JSON-LD schema.org) por página.

Consolida os nós num único ``@graph`` para evitar múltiplos blocos e duplicação.
Todo nó usa o host canônico (ver [[seo-canonical-host]]); nunca ``www``.

- ``EducationalOrganization`` em todas as páginas (identifica a escola para o Google).
- ``BreadcrumbList`` nas páginas internas (trilha Início > Página).
"""

from django.conf import settings

# Rótulo curto de cada rota, usado na trilha de breadcrumb.
BREADCRUMB_LABELS = {
    "about": "Sobre",
    "contato": "Agende uma Visita",
    "educacaoInfantil": "Educação Infantil",
    "ensinoFundamental": "Ensino Fundamental 1",
    "ensinoFundamental2": "Ensino Fundamental 2",
    "ensinoMedio": "Ensino Médio",
    "ensinoIntegral": "Ensino Integral",
}


def _base_url():
    return f"https://{settings.CANONICAL_HOST}"


def organization_node(base):
    """Escola como EducationalOrganization (evolui o Organization antigo)."""
    return {
        "@type": "EducationalOrganization",
        "@id": f"{base}/#organization",
        "name": "Centro Educacional Logos",
        "url": f"{base}/",
        "logo": f"{base}/static/images/logo/logo-1.svg",
        "telephone": "+55-91-3013-0198",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "Passagem Miranda, 300 - Coqueiro",
            "addressLocality": "Ananindeua",
            "addressRegion": "PA",
            "postalCode": "67113-200",
            "addressCountry": "BR",
        },
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": "+55-91-3013-0198",
            "contactType": "Customer Service",
        },
    }


def breadcrumb_node(url_name, path, base):
    """Trilha Início > Página para rotas internas; ``None`` na home/desconhecidas."""
    label = BREADCRUMB_LABELS.get(url_name)
    if not label:
        return None
    return {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {
                "@type": "ListItem",
                "position": 1,
                "name": "Início",
                "item": f"{base}/",
            },
            {
                "@type": "ListItem",
                "position": 2,
                "name": label,
                "item": f"{base}{path}",
            },
        ],
    }


def get_structured_data(url_name, path):
    """Monta o documento JSON-LD (``@graph``) da página atual."""
    base = _base_url()
    graph = [organization_node(base)]
    crumbs = breadcrumb_node(url_name, path, base)
    if crumbs:
        graph.append(crumbs)
    return {"@context": "https://schema.org", "@graph": graph}
