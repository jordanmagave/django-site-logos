"""Value objects do domínio de leads.

Todos imutáveis (frozen dataclasses ou tuplas), com validação em __post_init__.
Sem dependências externas (apenas stdlib).
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any
from urllib.parse import parse_qs, urlparse

from src.domain.errors import InvalidEmailError, InvalidPhoneError

_EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
_DIGITS_REGEX = re.compile(r"\D")

# Telefone: minimo 8 digitos (fixo regional) ate 15 (E.164).
_PHONE_MIN_DIGITS = 8
_PHONE_MAX_DIGITS = 15


@dataclass(frozen=True, slots=True)
class Email:
    """E-mail normalizado e validado."""

    value: str

    def __init__(self, raw: str) -> None:
        normalized = (raw or "").strip().lower()
        if not _EMAIL_REGEX.match(normalized):
            raise InvalidEmailError(f"Email invalido: {raw!r}")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True)
class Phone:
    """Telefone normalizado para apenas dígitos."""

    digits: str

    def __init__(self, raw: str) -> None:
        digits = _DIGITS_REGEX.sub("", raw or "")
        if not (_PHONE_MIN_DIGITS <= len(digits) <= _PHONE_MAX_DIGITS):
            raise InvalidPhoneError(
                f"Telefone com {len(digits)} digitos, esperado entre "
                f"{_PHONE_MIN_DIGITS} e {_PHONE_MAX_DIGITS}: {raw!r}"
            )
        object.__setattr__(self, "digits", digits)


@dataclass(frozen=True, slots=True)
class AnonymousId:
    """Identificador anônimo do Segment (analytics.user().anonymousId())."""

    value: str

    def __post_init__(self) -> None:
        if not self.value:
            raise ValueError("AnonymousId nao pode ser vazio")


@dataclass(frozen=True, slots=True)
class MessageId:
    """ID determinístico para idempotência no Segment.

    Mesma combinação (email normalizado, janela de tempo) produz o mesmo MessageId.
    A janela é tipicamente o timestamp do início de uma janela de N minutos.
    """

    value: str

    @classmethod
    def for_lead(cls, *, email: str, window_ms: int) -> MessageId:
        normalized = (email or "").strip().lower()
        material = f"lead|{normalized}|{window_ms}"
        digest = hashlib.sha256(material.encode("utf-8")).hexdigest()
        return cls(value=f"lead-{digest[:32]}")


@dataclass(frozen=True, slots=True)
class TrackingParams:
    """Parâmetros de tracking (UTMs + clickIds + anonymous_id + fbp/fbc).

    Imutável. Não armazena URL nem PII.
    """

    utm_source: str | None = None
    utm_medium: str | None = None
    utm_campaign: str | None = None
    utm_term: str | None = None
    utm_content: str | None = None
    gclid: str | None = None
    fbclid: str | None = None
    gbraid: str | None = None
    wbraid: str | None = None
    fbp: str | None = None
    fbc: str | None = None
    anonymous_id: str | None = None
    lead_source: str | None = None

    # Lista canonica dos parametros tracked
    UTM_KEYS: tuple[str, ...] = field(
        default=(
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "gclid",
            "fbclid",
            "gbraid",
            "wbraid",
            "fbp",
            "fbc",
            "lead_source",
        ),
        init=False,
        repr=False,
        compare=False,
    )

    @classmethod
    def from_mapping(
        cls,
        data: dict[str, Any] | None,
        *,
        now_ms: int | None = None,
        url: str | None = None,
    ) -> TrackingParams:
        """Cria a partir de um dict.

        Corrige o typo `utm_campaing` -> `utm_campaign` (vem do payload Leadster).
        Se `url` for fornecido, gera `fbc` a partir de `fbclid` quando ausente.
        """
        data = data or {}

        def get(*keys: str) -> str | None:
            for k in keys:
                v = data.get(k)
                if v not in (None, ""):
                    return str(v)
            return None

        fbc = get("fbc")
        fbclid = get("fbclid")
        if not fbc and fbclid and url and now_ms is not None:
            fbc = _build_fbc(url=url, fbclid=fbclid, now_ms=now_ms)

        return cls(
            utm_source=get("utm_source"),
            utm_medium=get("utm_medium"),
            # 'utm_campaign' tem prioridade sobre 'utm_campaing' (typo Leadster)
            utm_campaign=get("utm_campaign", "utm_campaing"),
            utm_term=get("utm_term"),
            utm_content=get("utm_content"),
            gclid=get("gclid"),
            fbclid=fbclid,
            gbraid=get("gbraid"),
            wbraid=get("wbraid"),
            fbp=get("fbp"),
            fbc=fbc,
            anonymous_id=get("segment_anonymous_id", "anonymous_id"),
            lead_source=get("lead_source"),
        )

    @classmethod
    def from_url(cls, url: str, *, now_ms: int | None = None) -> TrackingParams:
        """Extrai tracking params da query string de uma URL."""
        if not url:
            return cls()
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        flat: dict[str, Any] = {k: v[0] for k, v in qs.items() if v}
        return cls.from_mapping(flat, now_ms=now_ms, url=url)


def _build_fbc(*, url: str, fbclid: str, now_ms: int) -> str:
    """Constroi cookie _fbc no formato fb.<subdomain>.<creation_ms>.<fbclid>.

    subdomain = 2 quando host comeca com 'www.', senao 1.
    """
    host = urlparse(url).netloc.lower()
    subdomain = 2 if host.startswith("www.") else 1
    return f"fb.{subdomain}.{now_ms}.{fbclid}"
