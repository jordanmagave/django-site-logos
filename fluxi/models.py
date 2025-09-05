from django.db import models
from django.core.validators import RegexValidator


class agendarVisita(models.Model):

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
