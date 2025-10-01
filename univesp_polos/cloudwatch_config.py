# Configuração do CloudWatch
CLOUDWATCH_CONFIG = {
    'ENABLED': True,  # Habilitado por padrão em produção
    'NAMESPACE': 'UnivespPolos/Metricas',
    'METRICS_COLLECTION_INTERVAL': 300,  # 5 minutos
    'ENABLE_BUSINESS_METRICS': True,
    'LOG_FAILURES': True,
}

# Configuração de Logging para métricas
CLOUDWATCH_LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'cloudwatch': {
            'class': 'watchtower.CloudWatchLogHandler',
            'log_group': 'UnivespPolos',
            'log_group_retention_days': 30,
            'use_queues': True,
            'send_interval': 60,
            'create_log_group': True,
        },
    },
    'loggers': {
        'polos.metrics': {
            'handlers': ['console', 'cloudwatch'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

# Configuração de Alertas
CLOUDWATCH_ALERTS = {
    'ErrorRate': {
        'metric_name': 'Errors',
        'threshold': 10,
        'period': 300,
        'evaluation_periods': 2,
        'comparison_operator': 'GreaterThanThreshold',
        'actions': ['SNS_TOPIC_ARN'],  # Configurar ARN do tópico SNS
    },
    'HighLatency': {
        'metric_name': 'Latency',
        'threshold': 2000,  # 2 segundos
        'period': 300,
        'evaluation_periods': 2,
        'comparison_operator': 'GreaterThanThreshold',
        'actions': ['SNS_TOPIC_ARN'],
    },
    'LowUserSatisfaction': {
        'metric_name': 'MediaGeralAvaliacoes',
        'threshold': 3.0,
        'period': 3600,  # 1 hora
        'evaluation_periods': 1,
        'comparison_operator': 'LessThanThreshold',
        'actions': ['SNS_TOPIC_ARN'],
    },
}

# Dashboards
CLOUDWATCH_DASHBOARDS = {
    'MainDashboard': {
        'name': 'UnivespPolos-Overview',
        'widgets': [
            {
                'type': 'metric',
                'title': 'Usuários Ativos',
                'metrics': ['UnivespPolos/Metricas/UsuariosAtivos'],
                'period': 3600,
                'stat': 'Average',
            },
            {
                'type': 'metric',
                'title': 'Taxa de Erro',
                'metrics': ['UnivespPolos/Metricas/Errors'],
                'period': 300,
                'stat': 'Sum',
            },
            {
                'type': 'metric',
                'title': 'Latência',
                'metrics': ['UnivespPolos/Metricas/Latency'],
                'period': 60,
                'stat': 'Average',
            },
            {
                'type': 'metric',
                'title': 'Satisfação dos Usuários',
                'metrics': ['UnivespPolos/Metricas/MediaGeralAvaliacoes'],
                'period': 3600,
                'stat': 'Average',
            },
        ],
    },
}
