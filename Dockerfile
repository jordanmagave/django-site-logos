# Dockerfile Simplificado

FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential libpq-dev

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput --clear

EXPOSE 8080

# Comando direto para iniciar o Gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 fluxi.wsgi:application