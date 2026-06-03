"""Configuração compartilhada de pytest.

Garante:
- Django configurado antes de qualquer import de módulos do framework.
- Banco SQLite em memória para os testes (não toca no banco real).
- src/ no sys.path para imports absolutos (from src.domain...).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import django

# Adiciona a raiz do projeto ao sys.path para que 'from src.domain...' funcione.
_ROOT = Path(__file__).resolve().parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def pytest_configure() -> None:
    """Inicializa Django uma única vez por sessão de testes."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "fluxi.settings")
    os.environ.setdefault("DEBUG", "True")
    os.environ.setdefault("SECRET_KEY", "test-secret-key-not-for-production")
    django.setup()
