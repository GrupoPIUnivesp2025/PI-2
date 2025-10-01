"""
Configurações de produção para o projeto UNIVESP Polos.
Este arquivo deve ser usado em ambiente de produção.
"""

from .settings import *
import os
from django.core.management.utils import get_random_secret_key

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Hosts permitidos
ALLOWED_HOSTS = [
    '.univesp-polos.com.br',  # Domínio principal e subdomínios
    '.amazonaws.com',         # Para URLs da AWS
]

# Configurações de Segurança
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 ano
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
X_FRAME_OPTIONS = 'DENY'

# Configurações de Arquivos Estáticos
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = f'https://static.{os.environ.get("DOMAIN_NAME", "univesp-polos.com.br")}/'

MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')
MEDIA_URL = f'https://static.{os.environ.get("DOMAIN_NAME", "univesp-polos.com.br")}/media/'

# AWS S3 para arquivos estáticos
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = f'{PROJECT_NAME}-{ENVIRONMENT}-static'
AWS_S3_CUSTOM_DOMAIN = f'static.{os.environ.get("DOMAIN_NAME", "univesp-polos.com.br")}'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=31536000',  # 1 ano
}
AWS_DEFAULT_ACL = None  # Desabilitado pois usamos bucket policy
AWS_LOCATION = ''  # Raiz do bucket
AWS_S3_REGION_NAME = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
AWS_S3_USE_SSL = True
AWS_S3_VERIFY = True

# Configurações de cache do CloudFront
AWS_S3_CUSTOM_DOMAIN = os.environ.get('CLOUDFRONT_DOMAIN', AWS_S3_CUSTOM_DOMAIN)
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/'
MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# Compressão de arquivos estáticos
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# Cache-busting para arquivos estáticos
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

# Storages
STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'

# AWS IAM
USE_AWS_IAM = True
AWS_DEFAULT_REGION = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')

# Banco de dados
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'univesp_polos'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
            'ssl': {
                'ca': '/etc/ssl/certs/rds-ca-2019-root.pem'
            }
        }
    }
}

# Cache
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Sessões
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'noreply@univesp-polos.com.br'

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': '/var/log/univesp_polos/django.log',
            'formatter': 'verbose',
        },
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# Configurações adicionais de segurança
CSRF_TRUSTED_ORIGINS = [
    'https://*.univesp-polos.com.br',
    'https://*.amazonaws.com',
]

# Tempo de expiração da sessão (2 horas)
SESSION_COOKIE_AGE = 7200
