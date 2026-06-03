"""Erros do domínio (não acoplados a framework)."""

from __future__ import annotations


class DomainError(Exception):
    """Erro base do domínio. Subclasses representam violações de regra."""


class InvalidEmailError(DomainError):
    """E-mail em formato inválido."""


class InvalidPhoneError(DomainError):
    """Telefone em formato inválido."""


class InvalidLeadPayloadError(DomainError):
    """Payload de lead com campos obrigatórios ausentes ou inválidos."""


class InvalidWebhookSignatureError(DomainError):
    """Assinatura HMAC do webhook não confere."""
