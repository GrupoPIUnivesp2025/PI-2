#!/bin/bash

# Script para Disaster Recovery do UNIVESP Polos
# Implementa recuperação automática em caso de falha da região principal

# Configurações
NOME_PROJETO="univesp-polos"
AMBIENTE=${1:-"prod"}
REGIAO_PRINCIPAL="us-east-1"
REGIAO_DR="us-west-2"  # Região de backup
PREFIXO_STACK="${NOME_PROJETO}-${AMBIENTE}"

# Função para verificar saúde da aplicação
verificar_saude() {
    local url=$1
    local max_tentativas=$2
    local tentativa=1
    
    while [ $tentativa -le $max_tentativas ]; do
        if curl -s -f "${url}/health/" > /dev/null; then
            return 0
        fi
        echo "Tentativa $tentativa de $max_tentativas falhou..."
        sleep 10
        tentativa=$((tentativa + 1))
    done
    return 1
}

# Função para ativar região DR
ativar_dr() {
    echo "Ativando região de DR..."
    
    # 1. Atualizar Route 53
    aws route53 change-resource-record-sets \
        --hosted-zone-id $HOSTED_ZONE_ID \
        --change-batch '{
            "Changes": [{
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": "'$DOMAIN_NAME'",
                    "Type": "A",
                    "AliasTarget": {
                        "HostedZoneId": "'$DR_ALB_ZONE_ID'",
                        "DNSName": "'$DR_ALB_DNS'",
                        "EvaluateTargetHealth": true
                    }
                }
            }]
        }'
    
    # 2. Escalar serviço DR
    aws ecs update-service \
        --cluster "${PREFIXO_STACK}-cluster" \
        --service "${PREFIXO_STACK}-service" \
        --desired-count $DESIRED_COUNT \
        --region $REGIAO_DR
    
    # 3. Ativar réplica de leitura como master
    aws rds promote-read-replica \
        --db-cluster-identifier "${PREFIXO_STACK}-aurora-dr" \
        --region $REGIAO_DR
}

# Função para restaurar região principal
restaurar_principal() {
    echo "Restaurando região principal..."
    
    # 1. Sincronizar dados do DR para principal
    aws rds start-db-cluster-export-task \
        --db-cluster-identifier "${PREFIXO_STACK}-aurora-dr" \
        --s3-bucket-name "${PREFIXO_STACK}-dr-backup" \
        --region $REGIAO_DR
    
    # Aguardar exportação
    aws rds wait db-cluster-export-task-available \
        --source-arn $EXPORT_TASK_ARN \
        --region $REGIAO_DR
    
    # 2. Restaurar dados na região principal
    aws rds restore-db-cluster-from-s3 \
        --db-cluster-identifier "${PREFIXO_STACK}-aurora" \
        --s3-bucket-name "${PREFIXO_STACK}-dr-backup" \
        --region $REGIAO_PRINCIPAL
    
    # 3. Reverter Route 53
    aws route53 change-resource-record-sets \
        --hosted-zone-id $HOSTED_ZONE_ID \
        --change-batch '{
            "Changes": [{
                "Action": "UPSERT",
                "ResourceRecordSet": {
                    "Name": "'$DOMAIN_NAME'",
                    "Type": "A",
                    "AliasTarget": {
                        "HostedZoneId": "'$PRIMARY_ALB_ZONE_ID'",
                        "DNSName": "'$PRIMARY_ALB_DNS'",
                        "EvaluateTargetHealth": true
                    }
                }
            }]
        }'
}

# Monitoramento contínuo
while true; do
    if ! verificar_saude $PRIMARY_URL 3; then
        echo "Falha detectada na região principal!"
        
        # Verificar se é problema de aplicação ou região
        if aws health describe-events --region $REGIAO_PRINCIPAL --filter eventTypeCategories=issue,scheduledChange --query 'events[].{Type:eventTypeCode,Status:statusCode}' --output text | grep -q "AWS_"; then
            echo "Problema detectado na AWS região $REGIAO_PRINCIPAL"
            ativar_dr
            
            # Monitorar recuperação da região principal
            while true; do
                if ! aws health describe-events --region $REGIAO_PRINCIPAL --filter eventTypeCategories=issue --query 'events[].{Type:eventTypeCode,Status:statusCode}' --output text | grep -q "AWS_"; then
                    echo "Região principal recuperada"
                    restaurar_principal
                    break
                fi
                sleep 300  # Verificar a cada 5 minutos
            done
        else
            echo "Problema local da aplicação, aguardando auto-recuperação..."
            sleep 60
        fi
    fi
    sleep 30
done
