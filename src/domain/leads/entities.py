"""Entidades do domínio de leads."""

from __future__ import annotations

from dataclasses import dataclass

from src.domain.leads.value_objects import Email, Phone, TrackingParams


@dataclass(frozen=True, slots=True)
class GeoLocation:
    """Informações de localização geográfica de um lead."""

    city: str | None = None
    region: str | None = None
    country: str | None = None
    latitude: float | None = None
    longitude: float | None = None


# Módulo-level singletons para defaults imutáveis (evita RUF009)
_DFLT_TRACKING = TrackingParams()
_DFLT_GEO = GeoLocation()


@dataclass(frozen=True, slots=True)
class Lead:
    """Entidade que representa um lead capturado."""

    nome: str
    email: Email
    telefone: Phone | None = None
    tracking: TrackingParams = _DFLT_TRACKING
    captured_url: str | None = None
    ip_lead: str | None = None
    consentimento_analytics: bool = True
    location: GeoLocation = _DFLT_GEO
