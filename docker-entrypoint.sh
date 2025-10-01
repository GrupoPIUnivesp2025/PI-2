#!/bin/bash

# Script de entrada para o container Docker

set -e

# Função para aguardar o banco de dados
wait_for_db() {
    echo "Aguardando banco de dados..."
    while ! nc -z $DB_HOST $DB_PORT; do
        sleep 1
    done
    echo "Banco de dados disponível!"
}

# Aguardar banco de dados
wait_for_db

# Executar migrações
echo "Aplicando migrações..."
python manage.py migrate --noinput

# Coletar arquivos estáticos
echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Executar comando passado como argumento
echo "Iniciando aplicação..."
exec "$@"
