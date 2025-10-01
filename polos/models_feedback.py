from django.db import models

class UserFeedback(models.Model):
    FEEDBACK_TYPES = [
        ('sugestao', 'Sugestão'),
        ('problema', 'Problema'),
        ('elogio', 'Elogio'),
        ('acessibilidade', 'Problema de Acessibilidade'),
        ('outro', 'Outro'),
    ]

    nome = models.CharField('Nome', max_length=100)
    email = models.EmailField('E-mail', max_length=254)
    telefone = models.CharField('Telefone', max_length=20, blank=True, null=True)
    tipo_feedback = models.CharField('Tipo de Feedback', max_length=20, choices=FEEDBACK_TYPES)
    mensagem = models.TextField('Mensagem')
    pagina_origem = models.CharField('Página de Origem', max_length=255, help_text='Página onde o feedback foi enviado')
    data_envio = models.DateTimeField('Data de Envio', auto_now_add=True)
    status = models.CharField('Status', max_length=20, default='pendente', choices=[
        ('pendente', 'Pendente'),
        ('em_analise', 'Em Análise'),
        ('resolvido', 'Resolvido'),
        ('fechado', 'Fechado'),
    ])
    resposta = models.TextField('Resposta', blank=True, null=True)
    data_resposta = models.DateTimeField('Data da Resposta', null=True, blank=True)

    class Meta:
        verbose_name = 'Feedback'
        verbose_name_plural = 'Feedbacks'
        ordering = ['-data_envio']

    def __str__(self):
        return f"{self.tipo_feedback} - {self.nome} ({self.data_envio.strftime('%d/%m/%Y')})"
