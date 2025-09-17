from celery import shared_task
import rudderstack.analytics as rudderanalytics
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, acks_late=True, max_retries=3)
def send_rudderstack_event(self, properties, anonymous_id):
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

        logger.info(
            f"Tarefa Celery: Evento RudderStack enviado com sucesso para {properties.get('email')}"
        )
    except Exception as e:
        logger.error(f"Tarefa Celery: Falha ao enviar evento para RudderStack: {e}")
        raise self.retry(exc=e, countdown=60)  # Tenta novamente em 1 minuto
