"""Segment CDP adapter.

Envolve a biblioteca segment.analytics (analytics.identify, analytics.track).
Inicialização lazy: chame `init(write_key)` uma vez no startup.

Compatível com segment-analytics-python 2.x.
"""

from __future__ import annotations

import logging

import segment.analytics as analytics

logger = logging.getLogger(__name__)


_initialized = False


def init(write_key: str | None) -> None:
    """Inicializa o client Segment. Chamar no startup (settings.py ou middleware)."""
    global _initialized
    if _initialized:
        return
    if not write_key:
        logger.warning("SEGMENT_WRITE_KEY nao configurado — eventos CDP serao descartados")
        _initialized = True
        return
    analytics.write_key = write_key
    analytics.send = True
    analytics.debug = False
    _initialized = True
    logger.info("Segment CDP inicializado")


class SegmentCDP:
    """Implementação de CDPPort usando segment.analytics.

    message_id e timestamp sao passados via context/messageId para
    compatibilidade com a SDK.
    """

    def identify(
        self, user_id: str, traits: dict[str, object], context: dict[str, object] | None = None
    ) -> None:
        if not _initialized:
            logger.debug("Segment nao inicializado, identify ignorado")
            return
        try:
            analytics.identify(
                user_id=user_id,
                traits=traits,
                context=context or {},
            )
        except Exception:
            logger.exception("Erro ao enviar identify para Segment")

    def track(
        self,
        user_id: str,
        event: str,
        properties: dict[str, object] | None = None,
        context: dict[str, object] | None = None,
        message_id: str | None = None,
        timestamp: str | None = None,
    ) -> None:
        if not _initialized:
            logger.debug("Segment nao inicializado, track ignorado")
            return
        try:
            ctx = dict(context or {})
            if message_id:
                ctx["messageId"] = message_id
            analytics.track(
                user_id=user_id,
                event=event,
                properties=properties or {},
                context=ctx,
            )
        except Exception:
            logger.exception("Erro ao enviar track para Segment")
