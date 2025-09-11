from django.shortcuts import render, redirect
from .forms import ContatoForm
import rudderstack.analytics as rudderanalytics
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
            logger.info(f"Contato salvo no banco de dados: {instancia_contato.nome}")

            # --- Envio para o RudderStack ---
            try:

                # Prepara as propriedades para o evento
                properties = {
                    "nome": instancia_contato.nome,
                    "email": instancia_contato.email,
                    "telefone": instancia_contato.telefone,
                    "pagina_origem": request.path,
                }

                for key in tracking_params_keys:
                    if hasattr(instancia_contato, key) and getattr(
                        instancia_contato, key
                    ):
                        properties[key] = getattr(instancia_contato, key)
                """
                rudderanalytics.track(
                    anonymous_id=request.session.session_key,
                    event="Formulario de Contato Enviado",
                    properties=properties,
                )
                
                rudderanalytics.flush()
                """
                logger.info(
                    f"Evento RudderStack 'Formulario de Contato Enviado' enviado para {instancia_contato.email}"
                )

            except Exception as e:
                # Se algo der errado com o RudderStack, registra o erro mas não quebra o site
                logger.error(f"Falha ao enviar evento para RudderStack: {e}")

            return redirect("contato")
    else:
        form = ContatoForm()

    context = {
        "footer": "true",
        "header": "true",
        "form": form,
    }
    return render(request, "pages/contato.html", context)
