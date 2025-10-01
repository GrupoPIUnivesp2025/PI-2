from django.contrib import admin
from .models import Polo
from .models_feedback import UserFeedback

@admin.register(Polo)
class PoloAdmin(admin.ModelAdmin):
    list_display = ('nome', 'cidade', 'estado', 'email', 'telefone', 'data_cadastro')
    list_filter = ('estado', 'cidade')
    search_fields = ('nome', 'endereco', 'cidade', 'estado')
    readonly_fields = ('data_cadastro', 'ultima_atualizacao')
    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'email', 'telefone')
        }),
        ('Localização', {
            'fields': ('cep', 'endereco', 'numero', 'complemento', 'bairro', 'cidade', 'estado', 'latitude', 'longitude')
        }),
        ('Atividades UNIVESP', {
            'fields': ('cursos_oferecidos', 'horario_atendimento')
        }),
        ('Atividades Extras', {
            'fields': ('atividades_extras', 'atividades_esportivas')
        }),
        ('Informações do Sistema', {
            'fields': ('data_cadastro', 'ultima_atualizacao'),
            'classes': ('collapse',)
        }),
    )

@admin.register(UserFeedback)
class UserFeedbackAdmin(admin.ModelAdmin):
    list_display = ('nome', 'email', 'tipo_feedback', 'status', 'data_envio')
    list_filter = ('tipo_feedback', 'status', 'data_envio')
    search_fields = ('nome', 'email', 'mensagem')
    readonly_fields = ('data_envio', 'pagina_origem')
    fieldsets = (
        ('Informações do Usuário', {
            'fields': ('nome', 'email', 'telefone')
        }),
        ('Feedback', {
            'fields': ('tipo_feedback', 'mensagem', 'status')
        }),
        ('Informações do Sistema', {
            'fields': ('data_envio', 'pagina_origem'),
            'classes': ('collapse',)
        }),
    )
