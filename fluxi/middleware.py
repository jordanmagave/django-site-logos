# fluxi/middleware.py


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
