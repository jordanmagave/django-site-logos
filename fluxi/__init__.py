from .celery import app as celery_app

default_app_config = "fluxi.apps.FluxiConfig"

__all__ = ("celery_app",)
