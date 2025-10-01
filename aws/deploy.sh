#!/bin/bash

# Configurações
NOME_PROJETO="univesp-polos"
AMBIENTE=${1:-"prod"}  # Usa prod por padrão, mas aceita um parâmetro
REGIAO="us-east-1"
PREFIXO_STACK="${NOME_PROJETO}-${AMBIENTE}"

# Validar ambiente
if [[ ! "$AMBIENTE" =~ ^(prod|staging)$ ]]; then
    echo "Ambiente inválido. Use 'prod' ou 'staging'."
    exit 1
fi

# Função para aguardar a conclusão da stack
aguardar_stack() {
    local nome_stack=$1
    echo "Aguardando conclusão da stack $nome_stack..."
    aws cloudformation wait stack-create-complete --stack-name $nome_stack --region $REGIAO
    if [ $? -eq 0 ]; then
        echo "Stack $nome_stack criada com sucesso!"
    else
        echo "Erro na criação da stack $nome_stack"
        exit 1
    fi
}

# 1. Implantação da VPC e infraestrutura de rede
echo "Criando stack de rede..."
aws cloudformation create-stack \
    --stack-name "${PREFIXO_STACK}-network" \
    --template-body file://network.yaml \
    --parameters \
        ParameterKey=Environment,ParameterValue=$AMBIENTE \
        ParameterKey=ProjectName,ParameterValue=$NOME_PROJETO \
    --capabilities CAPABILITY_IAM \
    --region $REGIAO

aguardar_stack "${PREFIXO_STACK}-network"

# 2. Implantação do banco de dados Aurora
echo "Criando stack do banco de dados..."
aws cloudformation create-stack \
    --stack-name "${PREFIXO_STACK}-database" \
    --template-body file://database.yaml \
    --parameters \
        ParameterKey=Environment,ParameterValue=$AMBIENTE \
        ParameterKey=ProjectName,ParameterValue=$NOME_PROJETO \
        ParameterKey=DatabaseName,ParameterValue=univesp_polos \
        ParameterKey=DatabaseMasterUsername,ParameterValue=admin \
        ParameterKey=DatabaseMasterPassword,ParameterValue=$(openssl rand -base64 32) \
    --capabilities CAPABILITY_IAM \
    --region $REGIAO

aguardar_stack "${PREFIXO_STACK}-database"

# 3. Implantação da aplicação
echo "Criando stack da aplicação..."
aws cloudformation create-stack \
    --stack-name "${PREFIXO_STACK}-application" \
    --template-body file://application.yaml \
    --parameters \
        ParameterKey=Environment,ParameterValue=$AMBIENTE \
        ParameterKey=ProjectName,ParameterValue=$NOME_PROJETO \
        ParameterKey=DomainName,ParameterValue=univesp-polos.com.br \
        ParameterKey=ContainerImage,ParameterValue=$AWS_ACCOUNT_ID.dkr.ecr.$REGIAO.amazonaws.com/$NOME_PROJETO:latest \
        ParameterKey=CertificateArn,ParameterValue=$SSL_CERTIFICATE_ARN \
    --capabilities CAPABILITY_IAM \
    --region $REGIAO

aguardar_stack "${PREFIXO_STACK}-application"

# 4. Implantação dos recursos estáticos (S3 e CloudFront)
echo "Criando stack de recursos estáticos..."

# Validar email para alertas
read -p "Digite o email para receber alertas: " EMAIL_ALERTAS
if [[ ! "$EMAIL_ALERTAS" =~ ^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$ ]]; then
    echo "Email inválido"
    exit 1
fi
aws cloudformation create-stack \
    --stack-name "${PREFIXO_STACK}-static" \
    --template-body file://static_assets.yaml \
    --parameters \
        ParameterKey=Environment,ParameterValue=$AMBIENTE \
        ParameterKey=ProjectName,ParameterValue=$NOME_PROJETO \
        ParameterKey=DomainName,ParameterValue=univesp-polos.com.br \
        ParameterKey=CertificateArn,ParameterValue=$SSL_CERTIFICATE_ARN \
    --capabilities CAPABILITY_IAM \
    --region $REGIAO

aguardar_stack "${PREFIXO_STACK}-static"

# 5. Fazer upload dos arquivos estáticos para o S3
echo "Fazendo upload dos arquivos estáticos..."
BUCKET_ESTATICO=$(aws cloudformation describe-stacks --stack-name ${PREFIXO_STACK}-static --query 'Stacks[0].Outputs[?OutputKey==`StaticBucketName`].OutputValue' --output text --region $REGIAO)

# Coletar arquivos estáticos do Django
python manage.py collectstatic --no-input

# Upload para S3
aws s3 sync staticfiles/ s3://$BUCKET_ESTATICO/ --delete --cache-control "public, max-age=31536000"

# Invalidar cache do CloudFront
ID_DISTRIBUICAO=$(aws cloudfront list-distributions --query "DistributionList.Items[?Aliases.Items[?contains(@, 'static.${NOME_PROJETO}')]].Id" --output text)
aws cloudfront create-invalidation --distribution-id $ID_DISTRIBUICAO --paths "/*"

# 6. Implantação do monitoramento e backup
echo "Criando stack de monitoramento e backup..."
aws cloudformation create-stack \
    --stack-name "${PREFIXO_STACK}-monitoring" \
    --template-body file://monitoring.yaml \
    --parameters \
        ParameterKey=Environment,ParameterValue=$AMBIENTE \
        ParameterKey=ProjectName,ParameterValue=$NOME_PROJETO \
        ParameterKey=AlertEmail,ParameterValue=$EMAIL_ALERTAS \
    --capabilities CAPABILITY_IAM \
    --region $REGIAO

aguardar_stack "${PREFIXO_STACK}-monitoring"

echo "Implantação concluída com sucesso!"

# Exibir informações importantes
echo "Informações da Implantação:"
echo "-------------------------"
echo "Ambiente: $AMBIENTE"
echo "Endpoint do Banco de Dados: $(aws cloudformation describe-stacks --stack-name ${PREFIXO_STACK}-database --query 'Stacks[0].Outputs[?OutputKey==`ClusterEndpoint`].OutputValue' --output text --region $REGIAO)"
echo "URL da Aplicação: $(aws cloudformation describe-stacks --stack-name ${PREFIXO_STACK}-application --query 'Stacks[0].Outputs[?OutputKey==`ServiceUrl`].OutputValue' --output text --region $REGIAO)"
echo "URL dos Arquivos Estáticos: $(aws cloudformation describe-stacks --stack-name ${PREFIXO_STACK}-static --query 'Stacks[0].Outputs[?OutputKey==`StaticCDNURL`].OutputValue' --output text --region $REGIAO)"
echo "Dashboard de Monitoramento: $(aws cloudformation describe-stacks --stack-name ${PREFIXO_STACK}-monitoring --query 'Stacks[0].Outputs[?OutputKey==`MonitoringDashboardURL`].OutputValue' --output text --region $REGIAO)"
echo "Vault de Backup: $(aws cloudformation describe-stacks --stack-name ${PREFIXO_STACK}-monitoring --query 'Stacks[0].Outputs[?OutputKey==`BackupVaultName`].OutputValue' --output text --region $REGIAO)"
