# fluxi/urls.py

from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path
from django.views.generic import RedirectView
from fluxi import homeViews
from fluxi import pagesViews
from fluxi import servicesViews
from seo import views as seo_views
from seo.sitemaps import StaticViewSitemap

sitemaps = {"static": StaticViewSitemap}

urlpatterns = [
    path("admin/", admin.site.urls),
    # SEO
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    path("robots.txt", seo_views.robots_txt, name="robots_txt"),
    path("llms.txt", seo_views.llms_txt, name="llms_txt"),
    path("", homeViews.index, name="index"),
    path("about/", pagesViews.about, name="about"),
    path("contato/", pagesViews.contato, name="contato"),
    # Serviços educacionais
    path(
        "servicos-educacionais/educacao-infantil",
        servicesViews.infantil,
        name="educacaoInfantil",
    ),
    path(
        "servicos-educacionais/ensino-fundamental-1",
        servicesViews.fundamental1,
        name="ensinoFundamental",
    ),
    path(
        "servicos-educacionais/ensino-fundamental-2",
        servicesViews.fundamental2,
        name="ensinoFundamental2",
    ),
    path("servicos-educacionais/ensino-medio", servicesViews.medio, name="ensinoMedio"),
    path(
        "servicos-educacionais/integral", servicesViews.integral, name="ensinoIntegral"
    ),
    # Slug legado com underscore (ruim para SEO): 301 permanente para /contato/
    path(
        "contato_logos/",
        RedirectView.as_view(pattern_name="contato", permanent=True),
        name="contato_logos_legacy",
    ),
    path(
        "webhook/leadster/f9c1b2a3-d4e5-f6a7-b8c9-d0e1f2a3b4c5/",
        pagesViews.leadster_webhook,
        name="leadster_webhook",
    ),
]
