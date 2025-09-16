#!/bin/bash
echo "Iniciando o serviço Web (Gunicorn)..."
exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 fluxi.wsgi:application