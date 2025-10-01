from django.contrib.auth.backends import ModelBackend
from django.conf import settings
import boto3
from botocore.exceptions import ClientError
from .models_user import CustomUser

class CustomAuthBackend(ModelBackend):
    """
    Backend de autenticação personalizado que suporta tanto autenticação local
    quanto autenticação via AWS IAM
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        # Primeiro tenta autenticação local
        user = super().authenticate(request, username=username, password=password, **kwargs)
        if user:
            return user
            
        # Se não encontrou localmente e AWS está configurada, tenta AWS IAM
        if hasattr(settings, 'USE_AWS_IAM') and settings.USE_AWS_IAM:
            try:
                # Inicializa o cliente AWS IAM
                iam = boto3.client('iam',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_DEFAULT_REGION
                )
                
                # Verifica se o usuário existe no IAM
                try:
                    iam_user = iam.get_user(UserName=username)
                    
                    # Se chegou aqui, o usuário existe no IAM
                    # Procura ou cria o usuário local
                    user, created = CustomUser.objects.get_or_create(
                        username=username,
                        defaults={
                            'is_local_only': False,
                            'aws_iam_user_id': iam_user['User']['UserId'],
                            'is_staff': True,  # Usuários IAM são considerados staff
                        }
                    )
                    
                    if not created:
                        # Atualiza informações do usuário existente
                        user.aws_iam_user_id = iam_user['User']['UserId']
                        user.is_local_only = False
                        user.save()
                    
                    return user
                    
                except ClientError as e:
                    if e.response['Error']['Code'] == 'NoSuchEntity':
                        # Usuário não existe no IAM
                        return None
                    raise
                    
            except Exception as e:
                # Log do erro e fallback para None em caso de erro
                print(f"Erro na autenticação AWS IAM: {str(e)}")
                return None
        
        return None

    def get_user(self, user_id):
        try:
            return CustomUser.objects.get(pk=user_id)
        except CustomUser.DoesNotExist:
            return None
