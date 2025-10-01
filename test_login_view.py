from django.http import HttpResponse
from django.contrib.auth import get_user_model, authenticate, login as auth_login
from django.shortcuts import render, redirect

User = get_user_model()

def test_login(request):
    """View de teste para diagnosticar problemas de login"""
    
    if request.method == 'GET':
        # Criar usuário de teste se não existir
        try:
            user, created = User.objects.get_or_create(
                username='test',
                defaults={
                    'email': 'test@test.com',
                    'is_superuser': True,
                    'is_staff': True
                }
            )
            if created:
                user.set_password('test123')
                user.save()
                message = f"Usuário de teste criado: {user.username}"
            else:
                message = f"Usuário de teste já existe: {user.username}"
        except Exception as e:
            message = f"Erro ao criar usuário: {e}"
        
        # Listar todos os usuários
        users = User.objects.all()
        users_info = [f"{u.username} (ativo: {u.is_active}, staff: {u.is_staff})" for u in users]
        
        return HttpResponse(f"""
        <h1>Debug de Login</h1>
        <p>{message}</p>
        <h2>Usuários no sistema:</h2>
        <ul>{''.join([f'<li>{u}</li>' for u in users_info])}</ul>
        
        <h2>Teste de Login</h2>
        <form method="post">
            <input type="hidden" name="csrfmiddlewaretoken" value="{request.META.get('CSRF_COOKIE', '')}">
            <p>Usuário: <input type="text" name="username" value="test"></p>
            <p>Senha: <input type="password" name="password" value="test123"></p>
            <p><input type="submit" value="Testar Login"></p>
        </form>
        """)
    
    elif request.method == 'POST':
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            return HttpResponse(f"Login bem-sucedido! Usuário: {user.username}")
        else:
            return HttpResponse(f"Login falhou para usuário: {username}")
