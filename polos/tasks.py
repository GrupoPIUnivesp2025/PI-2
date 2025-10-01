from celery import shared_task
from django.conf import settings
from django.utils import timezone
from .metrics import coletar_metricas_gerais, enviar_metrica
import logging

logger = logging.getLogger('polos.metrics')

@shared_task
def task_coletar_metricas_gerais():
    """
    Task periódica para coletar métricas gerais do sistema
    """
    try:
        logger.info('Iniciando coleta de métricas gerais')
        coletar_metricas_gerais()
        logger.info('Coleta de métricas gerais concluída')
    except Exception as e:
        logger.error(f'Erro ao coletar métricas gerais: {e}')
        if settings.CLOUDWATCH_CONFIG['LOG_FAILURES']:
            enviar_metrica(
                'MetricsFailures',
                1,
                {'Type': 'GeneralMetrics'},
                'Count'
            )

@shared_task
def task_monitorar_performance():
    """
    Task para monitorar performance e latência da aplicação
    """
    try:
        from django.db import connection
        import time
        
        # Medindo latência do banco de dados
        start_time = time.time()
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        db_latency = (time.time() - start_time) * 1000  # em milissegundos
        
        enviar_metrica(
            'DatabaseLatency',
            db_latency,
            {'Database': 'Primary'},
            'Milliseconds'
        )
        
        # Outras métricas de performance podem ser adicionadas aqui
        
    except Exception as e:
        logger.error(f'Erro ao monitorar performance: {e}')
        if settings.CLOUDWATCH_CONFIG['LOG_FAILURES']:
            enviar_metrica(
                'MetricsFailures',
                1,
                {'Type': 'PerformanceMetrics'},
                'Count'
            )

@shared_task
def task_limpar_metricas_antigas():
    """
    Task para limpar métricas antigas do CloudWatch
    """
    try:
        import boto3
        from datetime import datetime, timedelta
        
        cloudwatch = boto3.client('cloudwatch')
        
        # Remove métricas mais antigas que 30 dias
        response = cloudwatch.delete_metrics(
            Namespace=settings.CLOUDWATCH_CONFIG['NAMESPACE'],
            EndTime=datetime.now() - timedelta(days=30)
        )
        
        logger.info('Limpeza de métricas antigas concluída')
        
    except Exception as e:
        logger.error(f'Erro ao limpar métricas antigas: {e}')
        if settings.CLOUDWATCH_CONFIG['LOG_FAILURES']:
            enviar_metrica(
                'MetricsFailures',
                1,
                {'Type': 'CleanupMetrics'},
                'Count'
            )

def configurar_alertas_cloudwatch():
    """
    Configura os alertas do CloudWatch conforme definido nas configurações
    """
    try:
        import boto3
        
        cloudwatch = boto3.client('cloudwatch')
        
        for nome_alerta, config in settings.CLOUDWATCH_ALERTS.items():
            cloudwatch.put_metric_alarm(
                AlarmName=f'UnivespPolos-{nome_alerta}',
                AlarmDescription=f'Alerta para {nome_alerta}',
                MetricName=config['metric_name'],
                Namespace=settings.CLOUDWATCH_CONFIG['NAMESPACE'],
                Period=config['period'],
                EvaluationPeriods=config['evaluation_periods'],
                Threshold=config['threshold'],
                ComparisonOperator=config['comparison_operator'],
                Statistic='Average',
                ActionsEnabled=True,
                AlarmActions=config['actions']
            )
            
        logger.info('Alertas do CloudWatch configurados com sucesso')
        
    except Exception as e:
        logger.error(f'Erro ao configurar alertas do CloudWatch: {e}')
        if settings.CLOUDWATCH_CONFIG['LOG_FAILURES']:
            enviar_metrica(
                'MetricsFailures',
                1,
                {'Type': 'AlertConfiguration'},
                'Count'
            )

def criar_dashboard():
    """
    Cria o dashboard principal no CloudWatch
    """
    try:
        import boto3
        import json
        
        cloudwatch = boto3.client('cloudwatch')
        
        for dashboard_name, config in settings.CLOUDWATCH_DASHBOARDS.items():
            cloudwatch.put_dashboard(
                DashboardName=config['name'],
                DashboardBody=json.dumps({
                    'widgets': config['widgets']
                })
            )
            
        logger.info('Dashboard do CloudWatch criado com sucesso')
        
    except Exception as e:
        logger.error(f'Erro ao criar dashboard do CloudWatch: {e}')
        if settings.CLOUDWATCH_CONFIG['LOG_FAILURES']:
            enviar_metrica(
                'MetricsFailures',
                1,
                {'Type': 'DashboardCreation'},
                'Count'
            )
