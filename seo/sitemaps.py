# seo/sitemaps.py
from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Sitemap das páginas públicas estáticas.

    Força o host canônico (settings.CANONICAL_HOST) e https, independente da
    tabela django_site — assim o sitemap nunca aponta para www nem example.com.
    """

    protocol = "https"
    changefreq = "monthly"
    priority = 0.7

    PAGES = [
        "index",
        "about",
        "contato",
        "educacaoInfantil",
        "ensinoFundamental",
        "ensinoFundamental2",
        "ensinoMedio",
        "ensinoIntegral",
    ]

    def get_domain(self, site=None):
        return settings.CANONICAL_HOST

    def items(self):
        return self.PAGES

    def location(self, item):
        return reverse(item)
