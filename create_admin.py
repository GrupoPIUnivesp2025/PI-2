#!/usr/bin/env python
import os
import django

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'univesp_polos.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Criar superuser
try:
    if User.objects.filter(username='admin').exists():
        print("Usuário 'admin' já existe")
        user = User.objects.get(username='admin')
        print(f"Usuário: {user.username}, Email: {user.email}, Superuser: {user.is_superuser}")
    else:
        user = User.objects.create_superuser('admin', 'admin@test.com', 'admin123')
        print(f"Superuser criado: {user.username}")
except Exception as e:
    print(f"Erro ao criar usuário: {e}")

# Listar todos os usuários
print("\nTodos os usuários:")
for user in User.objects.all():
    print(f"- {user.username} (superuser: {user.is_superuser}, ativo: {user.is_active})")
