# models.py
from django.db import models
from django.utils import timezone


class ResponsavelFinanceiro(models.Model):
    cpf = models.CharField(max_length=11, db_index=True)
    nome = models.CharField(max_length=200)
    email = models.EmailField(blank=True, null=True)
    data_atualizacao = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Responsável Financeiro"
        verbose_name_plural = "Responsáveis Financeiros"

    def __str__(self):
        return f"{self.nome} - {self.cpf}"


class Aluno(models.Model):
    codigo = models.CharField(max_length=50, unique=True)
    nome = models.CharField(max_length=200)
    responsavel = models.ForeignKey(
        ResponsavelFinanceiro, on_delete=models.CASCADE, related_name="alunos"
    )
    turma = models.CharField(max_length=50, blank=True)
    ativo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nome} ({self.codigo})"


class BoletoArquivo(models.Model):
    aluno = models.ForeignKey(Aluno, on_delete=models.CASCADE)
    nome_arquivo = models.CharField(max_length=255)
    mes_referencia = models.CharField(max_length=7)  # "2024-03"
    url_cloud = models.URLField(blank=True)  # URL do Cloud Storage
    tamanho = models.BigIntegerField(default=0)  # em bytes
    data_upload = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["aluno", "nome_arquivo"]
        ordering = ["-mes_referencia"]


class LogAcesso(models.Model):
    TIPO_CHOICES = [
        ("CONSULTA", "Consulta"),
        ("VISUALIZACAO", "Visualização"),
        ("DOWNLOAD", "Download"),
    ]

    cpf = models.CharField(max_length=11)
    arquivo = models.CharField(max_length=255, blank=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    data_hora = models.DateTimeField(default=timezone.now)
    ip = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)

    class Meta:
        verbose_name = "Log de Acesso"
        verbose_name_plural = "Logs de Acesso"
        ordering = ["-data_hora"]
