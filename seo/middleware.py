# seo/middleware.py
from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalHostMiddleware:
    """Redireciona 301 de ``www.<host>`` para o host canônico (sem www), em https.

    Fica no topo do MIDDLEWARE para que a normalização de host aconteça em um único
    salto (www http/https -> https não-www), evitando cadeias de redirect que o
    Semrush penaliza. O redirect HTTP->HTTPS do host canônico é feito pelo
    SecurityMiddleware (SECURE_SSL_REDIRECT).
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.canonical_host = getattr(settings, "CANONICAL_HOST", "celogos.com.br")

    def __call__(self, request):
        host = request.get_host().split(":")[0]
        if host == f"www.{self.canonical_host}":
            return HttpResponsePermanentRedirect(
                f"https://{self.canonical_host}{request.get_full_path()}"
            )
        return self.get_response(request)
