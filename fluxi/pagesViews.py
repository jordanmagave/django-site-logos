from django.shortcuts import render, redirect
from .forms import ContatoForm
import rudderstack.analytics as rudderanalytics
import logging
from .tasks import send_rudderstack_event

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

            request.session.save()  # Certifique-se de que a sessão está salva

            # --- Envio para o RudderStack ---
            try:

                # Prepara as propriedades para o evento
                properties = {
                    "nome": instancia_contato.nome,
                    "email": instancia_contato.email,
                    "telefone": instancia_contato.telefone,
                    "pagina_origem": request.path,
                }

                send_rudderstack_event.delay(properties, request.session.session_key)
                logger.info(
                    f"Tarefa Celery: Evento RudderStack agendado para {instancia_contato.email}"
                )
            except Exception as e:
                logger.error(f"Falha ao agendar tarefa Celery: {e}")

            return redirect("contato")
    else:
        form = ContatoForm()

    context = {
        "footer": "true",
        "header": "true",
        "form": form,
    }
    return render(request, "pages/contato.html", context)
