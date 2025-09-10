# Dockerfile

# Use a imagem oficial do Python como base
FROM python:3.13-slim

# Define variáveis de ambiente
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Define o diretório de trabalho
WORKDIR /app

# Copie o arquivo de dependências
COPY requirements.txt .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código do projeto para o container
COPY . .

# Colete os arquivos estáticos
RUN python manage.py collectstatic --noinput

# Expõe a porta que o Gunicorn irá rodar
EXPOSE 8080

# Comando para iniciar a aplicação com Gunicorn
# O Cloud Run define a variável de ambiente PORT, que usamos aqui.
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 fluxi.wsgi:application