from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """
    Modelo de usuário customizado que estende o AbstractUser do Django
    e adiciona campos específicos para integração com AWS IAM
    """
    aws_iam_user_id = models.CharField(
        _('AWS IAM User ID'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('ID do usuário no AWS IAM')
    )
    
    aws_iam_role = models.CharField(
        _('AWS IAM Role'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_('Role do usuário no AWS IAM')
    )
    
    last_aws_sync = models.DateTimeField(
        _('Última sincronização com AWS'),
        blank=True,
        null=True,
        help_text=_('Data e hora da última sincronização com AWS IAM')
    )
    
    is_local_only = models.BooleanField(
        _('Usuário Local'),
        default=True,
        help_text=_('Indica se o usuário é apenas local ou também existe no AWS IAM')
    )

    class Meta:
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')

    def __str__(self):
        return self.username

    def save(self, *args, **kwargs):
        if not self.is_local_only and not self.aws_iam_user_id:
            # Aqui poderia ser implementada a lógica de sincronização com AWS IAM
            pass
        super().save(*args, **kwargs)
