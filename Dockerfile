# Use uma imagem oficial do Python como base
FROM python:3.11-slim

# Defina variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DEBIAN_FRONTEND=noninteractive

# Crie e defina o diretório de trabalho
WORKDIR /app

# Instale as dependências do sistema
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        default-libmysqlclient-dev \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copie os arquivos de requisitos primeiro para aproveitar o cache do Docker
COPY requirements_prod.txt .

# Instale as dependências Python
RUN pip install --no-cache-dir -r requirements_prod.txt

# Copie o código da aplicação
COPY . .

# Copie o script de entrada
COPY docker-entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

# Exponha a porta
EXPOSE 8000

# Configure o script de entrada como ponto de entrada
ENTRYPOINT ["docker-entrypoint.sh"]

# Comando padrão
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "univesp_polos.wsgi:application"]
