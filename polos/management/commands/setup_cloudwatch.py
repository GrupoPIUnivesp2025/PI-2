from django.core.management.base import BaseCommand
from polos.tasks import configurar_alertas_cloudwatch, criar_dashboard
import logging

logger = logging.getLogger('polos.metrics')

class Command(BaseCommand):
    help = 'Configura os alertas e dashboards do CloudWatch'

    def handle(self, *args, **options):
        try:
            self.stdout.write('Configurando alertas do CloudWatch...')
            configurar_alertas_cloudwatch()
            self.stdout.write(self.style.SUCCESS('Alertas configurados com sucesso!'))

            self.stdout.write('Criando dashboard do CloudWatch...')
            criar_dashboard()
            self.stdout.write(self.style.SUCCESS('Dashboard criado com sucesso!'))

        except Exception as e:
            logger.error(f'Erro ao configurar CloudWatch: {e}')
            self.stdout.write(self.style.ERROR(f'Erro ao configurar CloudWatch: {e}'))
