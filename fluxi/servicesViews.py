from django.shortcuts import render


def infantil(request):
    data = {
        "header": "true",
        "footer": "true",
        "page_name": "servico_infantil",
        "local_name": "CTA_visita_infantil",
    }
    return render(request, "services/servico_infantil.html", data)


def fundamental1(request):
    data = {
        "header": "true",
        "footer": "false",
        "page_name": "servico_fundamental1",
        "local_name": "CTA_visita_fundamental1",
    }
    return render(request, "services/servico_fundamental1.html", data)


def fundamental2(request):
    data = {
        "header": "true",
        "footer": "false",
        "page_name": "servico_fundamental2",
        "local_name": "CTA_visita_fundamental2",
    }
    return render(request, "services/servico_fundamental2.html", data)


def medio(request):
    data = {
        "header": "true",
        "footer": "false",
        "page_name": "servico_medio",
        "local_name": "CTA_visita_medio",
    }
    return render(request, "services/servico_medio.html", data)


def integral(request):
    data = {
        "header": "true",
        "footer": "false",
        "page_name": "servico_integral",
        "local_name": "CTA_visita_integral",
    }
    return render(request, "services/servico_integral.html", data)
