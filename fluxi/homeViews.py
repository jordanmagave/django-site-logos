from django.shortcuts import render


def index(request):
    data = {
        "header": "true",
    }
    return render(request, "home/index.html", data)
