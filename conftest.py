"""Configuração compartilhada de pytest.

Garante:
- Django configurado antes de qualquer import de módulos do framework.
- Banco SQLite em memória para os testes (não toca no banco real).
"""

from __future__ import annotations

import os

import django


def pytest_configure() -> None:
    """Inicializa Django uma única vez por sessão de testes."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fluxi.settings")
    os.environ.setdefault("DEBUG", "True")
    os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
    django.setup()
