from django.conf import settings
from django.contrib import sitemaps
from django.urls import reverse


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.8
    changefreq = "weekly"
    protocol = "https"

    def get_domain(self, site=None):
        # Força o host canônico (sem www) independentemente do framework Sites.
        return getattr(settings, "CANONICAL_HOST", "celogos.com.br")

    def items(self):
        return [
            "index",
            "about",
            "contato",
            "educacaoInfantil",
            "ensinoFundamental",
            "ensinoFundamental2",
            "ensinoMedio",
            "ensinoIntegral",
        ]

    def location(self, item):
        return reverse(item)
