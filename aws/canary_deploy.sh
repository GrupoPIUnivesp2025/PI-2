#!/bin/bash

# Script para gerenciar implantações canary
# Implanta gradualmente a nova versão e monitora métricas de saúde

# Configurações
NOME_PROJETO="univesp-polos"
AMBIENTE=${1:-"prod"}
REGIAO="us-east-1"
PREFIXO_STACK="${NOME_PROJETO}-${AMBIENTE}"
PORCENTAGEM_INICIAL=10
INCREMENTO=20
TEMPO_AVALIACAO=300  # 5 minutos

# Função para obter métricas do CloudWatch
obter_metricas() {
    local servico=$1
    local janela=$2
    
    # Obter taxa de erros 5xx
    ERRO_5XX=$(aws cloudwatch get-metric-statistics \
        --namespace AWS/ApplicationELB \
        --metric-name HTTPCode_Target_5XX_Count \
        --dimensions Name=TargetGroup,Value=$servico \
        --start-time $(date -u -v-${janela}S "+%Y-%m-%dT%H:%M:%S") \
        --end-time $(date -u "+%Y-%m-%dT%H:%M:%S") \
        --period $janela \
        --statistics Sum \
        --region $REGIAO \
        --query 'Datapoints[0].Sum' \
        --output text)

    # Obter latência
    LATENCIA=$(aws cloudwatch get-metric-statistics \
        --namespace AWS/ApplicationELB \
        --metric-name TargetResponseTime \
        --dimensions Name=TargetGroup,Value=$servico \
        --start-time $(date -u -v-${janela}S "+%Y-%m-%dT%H:%M:%S") \
        --end-time $(date -u "+%Y-%m-%dT%H:%M:%S") \
        --period $janela \
        --statistics Average \
        --region $REGIAO \
        --query 'Datapoints[0].Average' \
        --output text)

    # Retorna 1 se as métricas estiverem ruins
    if (( $(echo "$ERRO_5XX > 5" | bc -l) )) || (( $(echo "$LATENCIA > 2" | bc -l) )); then
        return 1
    fi
    return 0
}

# Função para atualizar peso do target group
atualizar_peso() {
    local peso_azul=$1
    local peso_verde=$2
    
    aws elbv2 modify-listener-rule \
        --listener-arn $LISTENER_ARN \
        --rule-arn $RULE_ARN \
        --actions Type=forward,ForwardConfig="{TargetGroups=[{TargetGroupArn=$TG_AZUL,Weight=$peso_azul},{TargetGroupArn=$TG_VERDE,Weight=$peso_verde}]}" \
        --region $REGIAO
}

# Obter ARNs necessários
LISTENER_ARN=$(aws elbv2 describe-listeners \
    --load-balancer-arn $ALB_ARN \
    --region $REGIAO \
    --query 'Listeners[0].ListenerArn' \
    --output text)

RULE_ARN=$(aws elbv2 describe-rules \
    --listener-arn $LISTENER_ARN \
    --region $REGIAO \
    --query 'Rules[0].RuleArn' \
    --output text)

# Criar novo target group (verde)
TG_VERDE=$(aws elbv2 create-target-group \
    --name "${PREFIXO_STACK}-verde" \
    --protocol HTTP \
    --port 80 \
    --vpc-id $VPC_ID \
    --health-check-path /health/ \
    --region $REGIAO \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text)

# Target group atual (azul)
TG_AZUL=$(aws elbv2 describe-target-groups \
    --names "${PREFIXO_STACK}-azul" \
    --region $REGIAO \
    --query 'TargetGroups[0].TargetGroupArn' \
    --output text)

# Implantar nova versão no target group verde
echo "Implantando nova versão no ambiente verde..."
aws ecs update-service \
    --cluster $CLUSTER_ECS \
    --service "${SERVICO_ECS}-verde" \
    --task-definition $NOVA_TASK_DEF \
    --region $REGIAO

# Iniciar implantação canary
echo "Iniciando implantação canary..."
PESO_VERDE=$PORCENTAGEM_INICIAL
PESO_AZUL=$((100 - PESO_VERDE))

while [ $PESO_VERDE -lt 100 ]; do
    echo "Atualizando pesos: Verde=${PESO_VERDE}%, Azul=${PESO_AZUL}%"
    atualizar_peso $PESO_AZUL $PESO_VERDE
    
    echo "Monitorando métricas por ${TEMPO_AVALIACAO} segundos..."
    sleep $TEMPO_AVALIACAO
    
    if ! obter_metricas $TG_VERDE $TEMPO_AVALIACAO; then
        echo "Detectado problema! Revertendo para versão anterior..."
        atualizar_peso 100 0
        aws ecs update-service \
            --cluster $CLUSTER_ECS \
            --service "${SERVICO_ECS}-verde" \
            --task-definition $TASK_DEF_ATUAL \
            --region $REGIAO
        exit 1
    fi
    
    PESO_VERDE=$((PESO_VERDE + INCREMENTO))
    PESO_AZUL=$((100 - PESO_VERDE))
done

# Completar migração
echo "Canary bem-sucedido. Finalizando migração..."
atualizar_peso 0 100

# Atualizar o target group azul com a nova versão
aws ecs update-service \
    --cluster $CLUSTER_ECS \
    --service "${SERVICO_ECS}-azul" \
    --task-definition $NOVA_TASK_DEF \
    --region $REGIAO

echo "Implantação canary concluída com sucesso!"
