from django.apps import AppConfig


class FluxiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "fluxi"

    def ready(self):

        return super().ready()

    verbose_name = "Centro Educacional Logos"
