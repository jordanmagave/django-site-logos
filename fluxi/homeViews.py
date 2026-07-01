from django.shortcuts import render


def index(request):
    data = {
        "header": "true",
        "footer": "true",
        "page_title": "Centro Educacional Logos - Educação Cristã Integral em Ananindeua",
        "page_description": (
            "Centro Educacional Logos: escola cristã há 30 anos em"
            " Ananindeua. Educação Infantil, Ensino Fundamental e Médio."
            " TOP 10 ENEM Pará. Agende sua visita!"
        ),
        "page_canonical": "https://celogos.com.br",
    }
    return render(request, "home/index.html", data)
