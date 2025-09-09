from django.shortcuts import render, redirect
from .forms import ContatoForm


def about(request):
    """Renderiza a página sobre nós."""
    data = {
        "footer": "true",
    }
    return render(request, "pages/about.html", data)


def contato(request):
    """Renderiza e processa o formulário de contato."""
    if request.method == "POST":
        form = ContatoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("contato")  # Redireciona após o envio bem-sucedido
    else:
        form = ContatoForm()

    context = {
        "footer": "true",
        "header": "true",
        "form": form,
    }
    return render(request, "pages/contato.html", context)
