#!/bin/bash

# Este script decide qual processo iniciar.

# Se a variável SERVICE_TYPE for "worker", inicia o worker.
if [ "$SERVICE_TYPE" = "worker" ]; then
  echo "Iniciando o serviço de Worker do Celery..."
  # Inicia o servidor de verificação de saúde em segundo plano
  python health_check.py &
  # Inicia o worker do Celery em primeiro plano
  celery -A fluxi worker --loglevel=info

# Caso contrário, inicia o servidor web como padrão.
else
  echo "Iniciando o serviço Web (Gunicorn)..."
  exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 fluxi.wsgi:application
fi