from django.db import models
from django.core.validators import RegexValidator

# Create your models here.


class Contato(models.Model):
    """Modelo para agendamento de visitas."""

    nome = models.CharField(max_length=100)
    email = models.EmailField()
    telefone = models.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r"^\(\d{2}\) \d{5}-\d{4}$",
                message="O número deve estar no formato (99) 99999-9999.",
            )
        ],
    )

    def __str__(self):
        return f"{self.nome} - {self.telefone}"


class TrackingEvents(models.Model):
    """Modelo para rastreamento de interações."""

    utm_source = models.CharField(max_length=100, blank=True, null=True)
    utm_medium = models.CharField(max_length=100, blank=True, null=True)
    utm_campaign = models.CharField(max_length=100, blank=True, null=True)
    utm_term = models.CharField(max_length=100, blank=True, null=True)
    utm_content = models.CharField(max_length=100, blank=True, null=True)
    page_url = models.URLField(max_length=200, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Tracking {self.id} - {self.page_url}"


class TrackSession(models.Model):
    """Modelo para rastreamento de sessões."""

    session_id = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.session_id
