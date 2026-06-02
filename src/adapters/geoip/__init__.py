"""Adapter MaxMind GeoIP2 para GeoIPPort."""

from __future__ import annotations

import logging

import geoip2.database
from geoip2.errors import AddressNotFoundError

from src.domain.leads.entities import GeoLocation

logger = logging.getLogger(__name__)


class MaxMindGeoIP:
    """Implementa GeoIPPort usando o banco GeoLite2-City da MaxMind."""

    def __init__(self, reader: geoip2.database.Reader) -> None:
        self._reader = reader

    def lookup(self, ip: str) -> GeoLocation | None:
        if not ip or ip in ("127.0.0.1", "0.0.0.0", "::1"):
            return None
        try:
            response = self._reader.city(ip)
            return GeoLocation(
                city=response.city.name,
                region=response.subdivisions.most_specific.name if response.subdivisions else None,
                country=response.country.iso_code,
                latitude=response.location.latitude,
                longitude=response.location.longitude,
            )
        except AddressNotFoundError:
            logger.debug(f"IP nao encontrado no GeoIP: {ip}")
            return None
        except Exception:
            logger.exception(f"Erro ao consultar GeoIP para {ip}")
            return None
