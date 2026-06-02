# fluxi/urls.py

from django.contrib import admin
from django.urls import path
from fluxi import homeViews
from fluxi import pagesViews
from fluxi import servicesViews
from src.adapters.django import views as adapter_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", homeViews.index, name="index"),
    path("about/", pagesViews.about, name="about"),
    path("contato/", adapter_views.contato, name="contato"),
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
    path("servicos-educacionais/integral", servicesViews.integral, name="ensinoIntegral"),
    path(
        "webhook/leadster/f9c1b2a3-d4e5-f6a7-b8c9-d0e1f2a3b4c5/",
        adapter_views.leadster_webhook,
        name="leadster_webhook",
    ),
]
