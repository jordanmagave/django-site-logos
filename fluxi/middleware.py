# fluxi/middleware.py

from django.conf import settings
from django.http import HttpResponsePermanentRedirect


class CanonicalHostMiddleware:
    """301 de ``www.<host>`` para o host canônico (sem www), preservando path/query.

    Evita duplicação de conteúdo www x não-www no audit de SEO. O host canônico vem
    de ``settings.CANONICAL_HOST``.
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


class TrackingParamsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # Lista de parâmetros que queremos rastrear
        self.tracking_params = [
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "gclid",
            "fbclid",
        ]

    def __call__(self, request):
        # Itera sobre a lista de parâmetros de rastreamento
        for param in self.tracking_params:
            # Verifica se o parâmetro existe na URL da requisição atual (request.GET)
            if param in request.GET:
                # Se o parâmetro for encontrado, salva o valor dele na sessão do usuário.
                # A sessão "lembra" desse valor para as próximas páginas que o usuário visitar.
                request.session[param] = request.GET[param]

        # Continua o processamento normal da requisição, passando para a próxima camada
        response = self.get_response(request)
        # Adiciona o cabeçalho personalizado na resposta
        response["X-Custom-Header"] = "ValorPersonalizado"
        return response
