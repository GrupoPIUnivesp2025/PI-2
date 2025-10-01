from django.db import models
from django.core.exceptions import ValidationError
from .models_user import CustomUser
from .services import get_coordinates_from_address, get_address_from_cep

class Polo(models.Model):
    nome = models.CharField('Nome do Polo', max_length=200)
    cep = models.CharField('CEP', max_length=9)
    endereco = models.CharField('Endereço', max_length=255)
    numero = models.CharField('Número', max_length=20)
    complemento = models.CharField('Complemento', max_length=100, blank=True, null=True)
    bairro = models.CharField('Bairro', max_length=100)
    cidade = models.CharField('Cidade', max_length=100)
    estado = models.CharField('Estado', max_length=2)
    latitude = models.DecimalField('Latitude', max_digits=10, decimal_places=8, null=True, blank=True)
    longitude = models.DecimalField('Longitude', max_digits=11, decimal_places=8, null=True, blank=True)
    telefone = models.CharField('Telefone', max_length=20)
    email = models.EmailField('E-mail', max_length=254)
    
    # Atividades UNIVESP
    cursos_oferecidos = models.TextField('Cursos Oferecidos')
    horario_atendimento = models.TextField('Horário de Atendimento')
    
    # Atividades não vinculadas à UNIVESP
    atividades_extras = models.TextField('Atividades Extras', blank=True, null=True)
    atividades_esportivas = models.TextField('Atividades Esportivas', blank=True, null=True)
    
    data_cadastro = models.DateTimeField('Data de Cadastro', auto_now_add=True)
    ultima_atualizacao = models.DateTimeField('Última Atualização', auto_now=True)

    class Meta:
        verbose_name = 'Polo'
        verbose_name_plural = 'Polos'
        ordering = ['cidade', 'nome']

    def clean(self):
        """
        Valida e processa os dados do polo antes de salvar.
        - Formata o CEP
        - Obtém coordenadas se não fornecidas
        - Valida o formato do CEP
        """
        # Formata o CEP
        self.cep = self.cep.replace('-', '').replace('.', '')
        if len(self.cep) != 8:
            raise ValidationError({'cep': 'CEP deve conter 8 dígitos'})
        self.cep = f"{self.cep[:5]}-{self.cep[5:]}"
        
        # Se não houver coordenadas, tenta obtê-las
        if not self.latitude or not self.longitude:
            coords = get_coordinates_from_address(
                f"{self.endereco}, {self.numero}",
                self.cidade,
                self.estado
            )
            if coords:
                self.latitude = coords['latitude']
                self.longitude = coords['longitude']
            else:
                raise ValidationError(
                    'Não foi possível obter as coordenadas do endereço. '
                    'Por favor, verifique o endereço ou insira as coordenadas manualmente.'
                )
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nome} - {self.cidade}/{self.estado}"
