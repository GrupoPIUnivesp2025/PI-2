from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models_feedback import UserFeedback

def submit_feedback(request):
    if request.method == 'POST':
        try:
            # Coleta os dados do formulário
            feedback = UserFeedback(
                nome=request.POST.get('nome'),
                email=request.POST.get('email'),
                telefone=request.POST.get('telefone'),
                tipo_feedback=request.POST.get('tipo_feedback'),
                mensagem=request.POST.get('mensagem'),
                pagina_origem=request.META.get('HTTP_REFERER', 'Não informada'),
                data_envio=timezone.now()
            )
            feedback.save()
            
            # Envia mensagem de sucesso
            messages.success(
                request,
                'Feedback enviado com sucesso! Agradecemos sua contribuição.'
            )
            
            # Redireciona para a página inicial
            return redirect('index')
            
        except Exception as e:
            messages.error(
                request,
                'Erro ao enviar feedback. Por favor, tente novamente.'
            )
            return render(request, 'polos/feedback_form.html')
    
    return render(request, 'polos/feedback_form.html')
