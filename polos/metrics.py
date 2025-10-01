import os
from datetime import datetime
from typing import Dict, Any

import boto3
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Count
from django.contrib.auth.signals import user_logged_in, user_logged_out

# Configuração CloudWatch
cloudwatch = boto3.client('cloudwatch',
                         region_name=os.getenv('AWS_REGION', 'us-east-1'))

def enviar_metrica(nome_metrica: str, valor: float, dimensoes: Dict[str, str], unidade: str = 'Count') -> None:
    """
    Envia uma métrica para o CloudWatch
    """
    try:
        cloudwatch.put_metric_data(
            Namespace='UnivespPolos/Metricas',
            MetricData=[{
                'MetricName': nome_metrica,
                'Value': valor,
                'Unit': unidade,
                'Dimensions': [{'Name': k, 'Value': v} for k, v in dimensoes.items()]
            }]
        )
    except Exception as e:
        print(f"Erro ao enviar métrica {nome_metrica}: {e}")

def registrar_evento_negocio(categoria: str, acao: str, dados: Dict[str, Any]) -> None:
    """
    Registra um evento de negócio no CloudWatch
    """
    try:
        cloudwatch.put_metric_data(
            Namespace='UnivespPolos/Eventos',
            MetricData=[{
                'MetricName': f"{categoria}_{acao}",
                'Value': 1,
                'Unit': 'Count',
                'Dimensions': [{'Name': k, 'Value': str(v)} for k, v in dados.items()]
            }]
        )
    except Exception as e:
        print(f"Erro ao registrar evento {categoria}_{acao}: {e}")

# Métricas de Usuário
@receiver(user_logged_in)
def registrar_login(sender, user, request, **kwargs):
    enviar_metrica(
        'Logins',
        1,
        {'Ambiente': os.getenv('ENVIRONMENT', 'prod')}
    )

@receiver(user_logged_out)
def registrar_logout(sender, user, request, **kwargs):
    enviar_metrica(
        'Logouts',
        1,
        {'Ambiente': os.getenv('ENVIRONMENT', 'prod')}
    )

# Métricas de Polo
@receiver(post_save, sender='polos.Polo')
def registrar_alteracao_polo(sender, instance, created, **kwargs):
    acao = 'Criacao' if created else 'Atualizacao'
    registrar_evento_negocio(
        'Polo',
        acao,
        {
            'Municipio': instance.municipio,
            'Estado': instance.estado
        }
    )

# Métricas de Feedback
@receiver(post_save, sender='polos.Feedback')
def registrar_feedback(sender, instance, created, **kwargs):
    if created:
        enviar_metrica(
            'Feedbacks',
            1,
            {
                'Polo': instance.polo.nome,
                'Avaliacao': str(instance.avaliacao)
            }
        )
        
        # Calcular média de avaliações do polo
        media_avaliacoes = instance.polo.feedback_set.aggregate(
            avg_avaliacao=Avg('avaliacao')
        )['avg_avaliacao']
        
        enviar_metrica(
            'MediaAvaliacoes',
            media_avaliacoes,
            {'Polo': instance.polo.nome},
            'None'
        )

def coletar_metricas_gerais():
    """
    Coleta métricas gerais do sistema periodicamente
    """
    from polos.models import Polo, Feedback
    from django.contrib.auth.models import User
    
    # Métricas de Usuários
    total_usuarios = User.objects.count()
    usuarios_ativos = User.objects.filter(is_active=True).count()
    
    enviar_metrica('TotalUsuarios', total_usuarios, {'Tipo': 'Total'})
    enviar_metrica('UsuariosAtivos', usuarios_ativos, {'Tipo': 'Ativos'})
    
    # Métricas de Polos
    total_polos = Polo.objects.count()
    polos_por_estado = Polo.objects.values('estado').annotate(
        total=Count('id')
    )
    
    enviar_metrica('TotalPolos', total_polos, {'Tipo': 'Total'})
    
    for estado in polos_por_estado:
        enviar_metrica(
            'PolosPorEstado',
            estado['total'],
            {'Estado': estado['estado']}
        )
    
    # Métricas de Feedback
    total_feedbacks = Feedback.objects.count()
    media_geral = Feedback.objects.aggregate(
        avg_avaliacao=Avg('avaliacao')
    )['avg_avaliacao']
    
    enviar_metrica('TotalFeedbacks', total_feedbacks, {'Tipo': 'Total'})
    enviar_metrica(
        'MediaGeralAvaliacoes',
        media_geral or 0,
        {'Tipo': 'Geral'},
        'None'
    )
