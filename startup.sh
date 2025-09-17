# startup.sh - versão corrigida
#!/bin/bash

# Definir PORT se não estiver definido
export PORT=${PORT:-8080}

# Se a variável SERVICE_TYPE for "worker", inicia o worker.
if [ "$SERVICE_TYPE" = "worker" ]; then
  echo "Iniciando o serviço de Worker do Celery..."
  python health_check.py &
  celery -A fluxi worker --loglevel=info
else
  echo "Iniciando o serviço Web (Gunicorn)..."
  echo "Executando migrações..."
  python manage.py migrate --noinput
  
  echo "Coletando arquivos estáticos..."
  python manage.py collectstatic --noinput --clear
  
  echo "Iniciando Gunicorn na porta $PORT..."
  exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 fluxi.wsgi:application
fi