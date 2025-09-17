"""
URL configuration for fluxi project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path
from fluxi import homeViews
from fluxi import pagesViews
from fluxi import servicesViews

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", homeViews.index, name="index"),
    path("about/", pagesViews.about, name="about"),
    # Logos
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
    path("contato/", pagesViews.contato, name="contato"),
    path("politica-de-privacidade/", pagesViews.privacy, name="privacy"),
]
