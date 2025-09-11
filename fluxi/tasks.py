from celery import shared_task
import rudderstack.analytics as rudderanalytics
import logging

logger = logging.getLogger(__name__)


@shared_task
def send_rudderstack_event(properties, anonymous_id):
    """
    Esta tarefa roda em segundo plano e envia o evento para o RudderStack.
    """
    try:
        # A inicialização do SDK já acontece no apps.py, então não precisamos repetir.
        rudderanalytics.track(
            anonymous_id=anonymous_id,
            event="Formulario de Contato Enviado",
            properties=properties,
        )
        # Aqui, o shutdown() é SEGURO, pois não está travando uma requisição do usuário.
        rudderanalytics.shutdown()
        logger.info(
            f"Tarefa Celery: Evento RudderStack enviado com sucesso para {properties.get('email')}"
        )
    except Exception as e:
        logger.error(f"Tarefa Celery: Falha ao enviar evento para RudderStack: {e}")
