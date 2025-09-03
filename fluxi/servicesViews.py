from django.shortcuts import render


def infantil(request):
    data = {
        "header": "true",
        "footer": "false",
    }
    return render(request, "services/servico_infantil.html", data)


def fundamental1(request):
    data = {
        "header": "true",
        "footer": "false",
    }
    return render(request, "services/servico_fundamental1.html", data)


def fundamental2(request):
    data = {
        "header": "true",
        "footer": "false",
    }
    return render(request, "services/servico_fundamental2.html", data)


def medio(request):
    data = {
        "header": "true",
        "footer": "false",
    }
    return render(request, "services/servico_medio.html", data)


def integral(request):
    data = {
        "header": "true",
        "footer": "false",
    }
    return render(request, "services/servico_integral.html", data)
