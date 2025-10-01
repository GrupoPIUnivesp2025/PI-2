from django.shortcuts import render, get_object_or_404, redirect
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from django.http import JsonResponse, HttpResponseForbidden
from .models import Polo
from .models_feedback import UserFeedback
from django.db.models import F
from django.contrib import messages
from .services import get_coordinates_from_address, get_address_from_cep, calculate_distance
import json

def index(request):
    """Página inicial do site"""
    return render(request, 'polos/index.html')

class PoloListView(ListView):
    """Lista todos os polos"""
    model = Polo
    template_name = 'polos/polo_list.html'
    context_object_name = 'polos'
    paginate_by = 10

class PoloDetailView(DetailView):
    """Exibe detalhes de um polo específico"""
    model = Polo
    template_name = 'polos/polo_detail.html'
    context_object_name = 'polo'

class StaffRequiredMixin(UserPassesTestMixin):
    """Mixin para verificar se o usuário é da equipe administrativa"""
    def test_func(self):
        return self.request.user.is_staff

class PoloCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    """Criar novo polo - apenas para administradores"""
    model = Polo
    template_name = 'polos/polo_form.html'
    fields = ['nome', 'cep', 'endereco', 'numero', 'complemento', 'bairro', 
              'cidade', 'estado', 'latitude', 'longitude', 'telefone', 'email',
              'cursos_oferecidos', 'horario_atendimento', 'atividades_extras',
              'atividades_esportivas']
    success_url = reverse_lazy('polo_list')
    
    def handle_no_permission(self):
        messages.error(self.request, 'Acesso restrito aos administradores do sistema.')
        return redirect('polo_list')

    def form_valid(self, form):
        messages.success(self.request, 'Polo criado com sucesso!')
        return super().form_valid(form)

class PoloUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    """Atualizar polo existente"""
    model = Polo
    template_name = 'polos/polo_form.html'
    fields = ['nome', 'cep', 'endereco', 'numero', 'complemento', 'bairro', 
              'cidade', 'estado', 'latitude', 'longitude', 'telefone', 'email',
              'cursos_oferecidos', 'horario_atendimento', 'atividades_extras',
              'atividades_esportivas']
    
    def get_success_url(self):
        return reverse_lazy('polo_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        messages.success(self.request, 'Polo atualizado com sucesso!')
        return super().form_valid(form)

@require_http_methods(["GET"])
def acessibilidade(request):
    """Página de documentação de acessibilidade"""
    return render(request, 'acessibilidade.html')

@require_http_methods(["POST"])
def submit_feedback(request):
    """Recebe e processa feedback dos usuários"""
    try:
        data = json.loads(request.body)
        feedback = UserFeedback(
            user=request.user if request.user.is_authenticated else None,
            feedback_type=data.get('type'),
            description=data.get('description'),
            page_url=data.get('page_url'),
            browser_info=request.META.get('HTTP_USER_AGENT', '')
        )
        feedback.save()
        messages.success(request, 'Obrigado pelo seu feedback! Ele nos ajuda a melhorar o sistema.')
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def busca_por_cep(request):
    """Página de busca de polos por CEP"""
    if request.method == 'POST':
        cep_busca = request.POST.get('cep', '').replace('-', '')
        limite = int(request.POST.get('limite', 5))
        
        try:
            # Obtém dados do CEP
            dados_cep = get_address_from_cep(cep_busca)
            if dados_cep:
                # Obtém coordenadas do endereço
                coords = get_coordinates_from_address(
                    dados_cep['logradouro'],
                    dados_cep['localidade'],
                    dados_cep['uf']
                )
                
                if coords:
                    lat_origem = coords['latitude']
                    lon_origem = coords['longitude']
                
                    # Busca todos os polos e calcula a distância
                    polos = Polo.objects.all()
                    polos_com_distancia = []
                    
                    for polo in polos:
                        distancia = calculate_distance(
                            float(polo.latitude),
                            float(polo.longitude),
                            lat_origem,
                            lon_origem
                        )
                    
                    polos_com_distancia.append({
                        'polo': polo,
                        'distancia': distancia
                    })
                
                # Ordena os polos por distância e limita ao número especificado
                polos_ordenados = sorted(polos_com_distancia, key=lambda x: x['distancia'])[:int(limite)]
                
                return render(request, 'polos/busca_resultado.html', {
                    'polos': polos_ordenados,
                    'endereco_busca': f"{dados_cep['logradouro']}, {dados_cep['bairro']}, {dados_cep['localidade']}/{dados_cep['uf']}"
                })
            
            else:
                messages.error(request, 'CEP não encontrado.')
                
        except Exception as e:
            messages.error(request, 'Erro ao buscar CEP. Tente novamente.')
            
    return render(request, 'polos/busca_form.html')
