# health_check.py
import os
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer

# Obtém a porta da variável de ambiente PORT, com 8080 como padrão
PORT = int(os.environ.get("PORT", 8080))


class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        """Responde com sucesso (código 200) a qualquer requisição GET."""
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok")


if __name__ == "__main__":
    # Inicia um servidor HTTP simples na porta especificada
    with HTTPServer(("", PORT), HealthCheckHandler) as httpd:
        print(f"Servidor de health check rodando na porta {PORT}", file=sys.stderr)
        httpd.serve_forever()
