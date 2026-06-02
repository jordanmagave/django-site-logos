"""Adapters stdlib: ClockPort, IdGeneratorPort, WebhookVerifierPort."""

from __future__ import annotations

import hashlib
import hmac
import time
import uuid


class SystemClock:
    """ClockPort que retorna o timestamp real do sistema."""

    def now_ms(self) -> int:
        return int(time.time() * 1000)


class UuidIdGenerator:
    """IdGeneratorPort que gera UUID v4."""

    def generate(self) -> str:
        return uuid.uuid4().hex


class HmacWebhookVerifier:
    """Verifica assinatura HMAC-SHA256 de webhooks."""

    def verify(self, payload: bytes, signature: str, secret: str) -> bool:
        expected = hmac.new(
            secret.encode("utf-8"),
            payload,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)
