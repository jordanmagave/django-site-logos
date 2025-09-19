from django.shortcuts import render


def index(request):
    data = {
        "header": "true",
        "footer": "true",
        "title": "Centro Educacional Logos - Formação Cristã Online",
    }
    return render(request, "home/index.html", data)
