from django.shortcuts import render


def about(request):
    """Renderiza a página sobre nós."""
    data = {"footer": "true"}
    return render(request, "pages/about.html", data)


def privacy(request):
    """Renderiza a página de política de privacidade."""
    data = {"header": "true", "footer": "true"}
    return render(request, "pages/privacyPolicy.html", data)
