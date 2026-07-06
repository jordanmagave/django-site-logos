from django.shortcuts import render

SERVICES_SEO = {
    "servico_infantil": {
        "page_name": "servico_infantil",
        "local_name": "CTA_visita_infantil",
        "page_title": "Educação Infantil - Centro Educacional Logos",
        "page_description": (
            "Educação Infantil de qualidade no Centro Educacional Logos"
            " em Ananindeua. Maternal ao Jardim 2 com desenvolvimento"
            " lúdico, acolhedor e valores cristãos."
        ),
        "page_canonical": "https://celogos.com.br/servicos-educacionais/educacao-infantil",
        "breadcrumb_items": [
            {
                "name": "Educação Infantil",
                "url": "https://celogos.com.br/servicos-educacionais/educacao-infantil",
            },
        ],
    },
    "servico_fundamental1": {
        "page_name": "servico_fundamental1",
        "local_name": "CTA_visita_fundamental1",
        "page_title": "Ensino Fundamental 1 - Centro Educacional Logos",
        "page_description": (
            "Ensino Fundamental I no Centro Educacional Logos: 1º ao 5º ano"
            " com material didático Mackenzie, formação acadêmica"
            " e princípios cristãos em Ananindeua."
        ),
        "page_canonical": "https://celogos.com.br/servicos-educacionais/ensino-fundamental-1",
        "breadcrumb_items": [
            {
                "name": "Ensino Fundamental 1",
                "url": "https://celogos.com.br/servicos-educacionais/ensino-fundamental-1",
            },
        ],
    },
    "servico_fundamental2": {
        "page_name": "servico_fundamental2",
        "local_name": "CTA_visita_fundamental2",
        "page_title": "Ensino Fundamental 2 - Centro Educacional Logos",
        "page_description": (
            "Ensino Fundamental II no Centro Educacional Logos: 5º ao 9º ano"
            " com robótica, laboratórios, esportes e preparação"
            " para os desafios do Ensino Médio em Ananindeua."
        ),
        "page_canonical": "https://celogos.com.br/servicos-educacionais/ensino-fundamental-2",
        "breadcrumb_items": [
            {
                "name": "Ensino Fundamental 2",
                "url": "https://celogos.com.br/servicos-educacionais/ensino-fundamental-2",
            },
        ],
    },
    "servico_medio": {
        "page_name": "servico_medio",
        "local_name": "CTA_visita_medio",
        "page_title": "Ensino Médio - Centro Educacional Logos",
        "page_description": (
            "Ensino Médio no Centro Educacional Logos: TOP 10 ENEM Pará,"
            " 7 anos consecutivos campeão em Ananindeua. Preparação"
            " intensiva para vestibular com valores cristãos."
        ),
        "page_canonical": "https://celogos.com.br/servicos-educacionais/ensino-medio",
        "breadcrumb_items": [
            {
                "name": "Ensino Médio",
                "url": "https://celogos.com.br/servicos-educacionais/ensino-medio",
            },
        ],
    },
    "servico_integral": {
        "page_name": "servico_integral",
        "local_name": "CTA_visita_integral",
        "page_title": "Ensino Integral - Centro Educacional Logos",
        "page_description": (
            "Período Integral no Centro Educacional Logos: atividades"
            " esportivas, artísticas, acompanhamento escolar e formação"
            " cristã em tempo integral em Ananindeua."
        ),
        "page_canonical": "https://celogos.com.br/servicos-educacionais/integral",
        "breadcrumb_items": [
            {
                "name": "Ensino Integral",
                "url": "https://celogos.com.br/servicos-educacionais/integral",
            },
        ],
    },
}


def infantil(request):
    data = {
        "header": "true",
        "footer": "true",
        "page_name": "servico_infantil",
        "local_name": "CTA_visita_infantil",
        **SERVICES_SEO["servico_infantil"],
    }
    return render(request, "services/servico_infantil.html", data)


def fundamental1(request):
    data = {
        "header": "true",
        "footer": "false",
        "page_name": "servico_fundamental1",
        "local_name": "CTA_visita_fundamental1",
        **SERVICES_SEO["servico_fundamental1"],
    }
    return render(request, "services/servico_fundamental1.html", data)


def fundamental2(request):
    data = {
        "header": "true",
        "footer": "false",
        "page_name": "servico_fundamental2",
        "local_name": "CTA_visita_fundamental2",
        **SERVICES_SEO["servico_fundamental2"],
    }
    return render(request, "services/servico_fundamental2.html", data)


def medio(request):
    data = {
        "header": "true",
        "footer": "false",
        "page_name": "servico_medio",
        "local_name": "CTA_visita_medio",
        **SERVICES_SEO["servico_medio"],
    }
    return render(request, "services/servico_medio.html", data)


def integral(request):
    data = {
        "header": "true",
        "footer": "false",
        "page_name": "servico_integral",
        "local_name": "CTA_visita_integral",
        **SERVICES_SEO["servico_integral"],
    }
    return render(request, "services/servico_integral.html", data)
