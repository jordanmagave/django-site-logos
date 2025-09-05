from django.shortcuts import render


def about(request):
    data = {
        "footer": "true",
    }
    return render(request, "pages/about.html", data)


def agendar_visita(request):
    data = {
        "footer": "true",
        "header": "true",
    }
    return render(request, "pages/bookDemo.html", data)
