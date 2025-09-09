# fluxi/middleware/tracking_middleware.py


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
        # Verifica se há parâmetros de rastreamento na URL (request.GET)
        for param in self.tracking_params:
            if param in request.GET:
                # Se um parâmetro for encontrado, salva ele na sessão do usuário
                request.session[param] = request.GET[param]

        # Continua o processamento normal da requisição
        response = self.get_response(request)
        return response
