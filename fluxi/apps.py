from django.apps import AppConfig


class FluxiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "fluxi"

    def ready(self):

        from django.conf import settings
        from rudderstack import analytics as rudderanalytics
        import logging

        logger = logging.getLogger(__name__)

        # Verifica se as chaves do rudderstack estão definidas
        if hasattr(settings, "RUDDERSTACK_PYTHON_WRITE_KEY") and hasattr(
            settings, "RUDDERSTACK_DATA_PLANE_URL"
        ):
            logger.info("Configurando RudderStack com as chaves do settings.py")
            rudderanalytics.write_key = settings.RUDDERSTACK_PYTHON_WRITE_KEY
            rudderanalytics.dataPlaneUrl = settings.RUDDERSTACK_DATA_PLANE_URL
            logger.info("RudderStack configurado com sucesso.")
        else:
            logger.warning("Chaves do RudderStack não encontradas no settings.py")

        return super().ready()

    verbose_name = "Centro Educacional Logos"
