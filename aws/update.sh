#!/bin/bash

# Script para atualização da aplicação UNIVESP Polos
# Este script atualiza a aplicação sem downtime usando implantação blue/green

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

# Função para aguardar a conclusão da atualização do serviço ECS
aguardar_atualizacao_servico() {
    local cluster=$1
    local servico=$2
    echo "Aguardando atualização do serviço..."
    aws ecs wait services-stable \
        --cluster $cluster \
        --services $servico \
        --region $REGIAO
}

# Função para validar saúde da aplicação
validar_saude() {
    local url=$1
    echo "Validando saúde da aplicação em $url..."
    for i in {1..30}; do
        if curl -s -f "${url}/health/" > /dev/null; then
            echo "Aplicação está saudável!"
            return 0
        fi
        echo "Tentativa $i: Aguardando aplicação ficar saudável..."
        sleep 10
    done
    echo "Erro: Aplicação não ficou saudável após 5 minutos"
    return 1
}

# Obter informações da stack
CLUSTER_ECS=$(aws cloudformation describe-stacks \
    --stack-name ${PREFIXO_STACK}-application \
    --query 'Stacks[0].Outputs[?OutputKey==`ECSCluster`].OutputValue' \
    --output text \
    --region $REGIAO)

SERVICO_ECS="${PREFIXO_STACK}-service"
URL_SERVICO=$(aws cloudformation describe-stacks \
    --stack-name ${PREFIXO_STACK}-application \
    --query 'Stacks[0].Outputs[?OutputKey==`URLServico`].OutputValue' \
    --output text \
    --region $REGIAO)

# 1. Construir e enviar nova imagem Docker
echo "Construindo nova imagem Docker..."
docker build -t ${NOME_PROJETO}:latest .

# Obter URI do repositório ECR
ECR_REPO="${AWS_ACCOUNT_ID}.dkr.ecr.${REGIAO}.amazonaws.com/${NOME_PROJETO}"

# Login no ECR
echo "Fazendo login no ECR..."
aws ecr get-login-password --region $REGIAO | docker login --username AWS --password-stdin $ECR_REPO

# Tag e push da imagem
echo "Enviando imagem para ECR..."
docker tag ${NOME_PROJETO}:latest ${ECR_REPO}:latest
docker push ${ECR_REPO}:latest

# 2. Atualizar serviço ECS
echo "Iniciando atualização do serviço ECS..."
aws ecs update-service \
    --cluster $CLUSTER_ECS \
    --service $SERVICO_ECS \
    --force-new-deployment \
    --region $REGIAO

# 3. Aguardar atualização e validar
aguardar_atualizacao_servico $CLUSTER_ECS $SERVICO_ECS
validar_saude $URL_SERVICO

if [ $? -eq 0 ]; then
    echo "Atualização concluída com sucesso!"
    
    # 4. Coletar e enviar arquivos estáticos
    echo "Atualizando arquivos estáticos..."
    
    # Coletar arquivos estáticos do Django
    python manage.py collectstatic --no-input

    # Obter nome do bucket
    BUCKET_ESTATICO=$(aws cloudformation describe-stacks \
        --stack-name ${PREFIXO_STACK}-static \
        --query 'Stacks[0].Outputs[?OutputKey==`StaticBucketName`].OutputValue' \
        --output text \
        --region $REGIAO)

    # Sincronizar com S3
    aws s3 sync staticfiles/ s3://$BUCKET_ESTATICO/ --delete --cache-control "public, max-age=31536000"

    # Invalidar cache do CloudFront
    ID_DISTRIBUICAO=$(aws cloudfront list-distributions \
        --query "DistributionList.Items[?Aliases.Items[?contains(@, 'static.${NOME_PROJETO}')]].Id" \
        --output text)
    aws cloudfront create-invalidation --distribution-id $ID_DISTRIBUICAO --paths "/*"

    echo "Arquivos estáticos atualizados e cache invalidado"
    echo "Implantação finalizada com sucesso!"
else
    echo "Erro na atualização. Iniciando rollback..."
    
    # Obter a última task definition estável
    ULTIMA_TASK_DEF=$(aws ecs describe-services \
        --cluster $CLUSTER_ECS \
        --services $SERVICO_ECS \
        --region $REGIAO \
        --query 'services[0].taskDefinition' \
        --output text)
    
    # Registrar nova revisão da última task definition estável
    ROLLBACK_TASK_DEF=$(aws ecs register-task-definition \
        --family $PREFIXO_STACK \
        --cli-input-json "$(aws ecs describe-task-definition \
            --task-definition $ULTIMA_TASK_DEF \
            --region $REGIAO \
            --query 'taskDefinition' \
            --output json)" \
        --region $REGIAO \
        --query 'taskDefinition.taskDefinitionArn' \
        --output text)
    
    # Atualizar serviço para a versão de rollback
    aws ecs update-service \
        --cluster $CLUSTER_ECS \
        --service $SERVICO_ECS \
        --task-definition $ROLLBACK_TASK_DEF \
        --region $REGIAO
    
    aguardar_atualizacao_servico $CLUSTER_ECS $SERVICO_ECS
    
    # Verificar saúde após rollback
    if validar_saude $URL_SERVICO; then
        echo "Rollback concluído com sucesso"
        # Notificar equipe sobre o rollback
        aws sns publish \
            --topic-arn "$SNS_TOPIC_ARN" \
            --subject "Rollback Executado: $AMBIENTE" \
            --message "Um rollback foi executado no ambiente $AMBIENTE devido a falha na atualização. Por favor, verifique os logs para mais detalhes."
    else
        echo "ERRO CRÍTICO: Rollback falhou. Intervenção manual necessária!"
        aws sns publish \
            --topic-arn "$SNS_TOPIC_ARN" \
            --subject "ALERTA CRÍTICO: Falha no Rollback - $AMBIENTE" \
            --message "O rollback falhou no ambiente $AMBIENTE. Intervenção manual necessária imediatamente!"
    fi
    exit 1
fi
