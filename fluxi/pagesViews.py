from django.shortcuts import render, redirect
from .forms import ContatoForm
import logging

# Configura um logger para ajudar a depurar
logger = logging.getLogger(__name__)


def about(request):
    """Renderiza a página sobre nós."""
    data = {"footer": "true"}
    return render(request, "pages/about.html", data)


def contato(request):
    """Renderiza e processa o formulário de contato."""
    if request.method == "POST":
        form = ContatoForm(request.POST)
        if form.is_valid():
            instancia_contato = form.save(commit=False)

            consent_given = form.cleaned_data.get("ketch_consent") == "true"
            instancia_contato.consentimento_analytics = consent_given
            # --- Captura dos Parâmetros de Rastreamento ---
            tracking_params_keys = [
                "utm_source",
                "utm_medium",
                "utm_campaign",
                "utm_term",
                "utm_content",
                "gclid",
                "fbclid",
            ]

            for key in tracking_params_keys:
                if key in request.session:
                    # Salva o valor da sessão no campo correspondente do modelo
                    setattr(instancia_contato, key, request.session.get(key))

            # Agora, salva a instância completa no banco de dados
            instancia_contato.save()
            logger.info(
                f"Contato salvo no banco de dados com consentimento: {consent_given}"
            )

            request.session.save()  # Certifique-se de que a sessão está salva

            return redirect("contato")
    else:
        form = ContatoForm()

    context = {
        "footer": "true",
        "header": "true",
        "form": form,
    }
    return render(request, "pages/contato.html", context)
