from django.shortcuts import render


def about(request):
    data = {
        "footer": "true",
    }
    return render(request, "pages/about.html", data)
