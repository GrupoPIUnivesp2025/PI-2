# Script para fazer backup manual do banco de dados
fazer_backup() {
    local ambiente=$1
    local descricao_backup="Backup manual - $(date +%Y-%m-%d_%H-%M-%S)"
    
    # Obter ID do cluster Aurora
    local id_cluster=$(aws rds describe-db-clusters \
        --query "DBClusters[?starts_with(DBClusterIdentifier, 'univesp-polos-${ambiente}')].DBClusterIdentifier" \
        --output text)
    
    if [ -z "$id_cluster" ]; then
        echo "Erro: Cluster não encontrado para o ambiente ${ambiente}"
        return 1
    fi
    
    # Criar snapshot
    aws rds create-db-cluster-snapshot \
        --db-cluster-identifier $id_cluster \
        --db-cluster-snapshot-identifier "manual-${ambiente}-$(date +%Y-%m-%d-%H-%M)" \
        --tags Key=Environment,Value=$ambiente Key=BackupType,Value=Manual \
        --region $AWS_DEFAULT_REGION
    
    echo "Backup iniciado para o cluster $id_cluster"
}

# Script para restaurar backup
restaurar_backup() {
    local ambiente=$1
    local id_snapshot=$2
    
    if [ -z "$id_snapshot" ]; then
        echo "Uso: restaurar_backup <ambiente> <id_snapshot>"
        return 1
    fi
    
    # Criar novo cluster a partir do snapshot
    aws rds restore-db-cluster-from-snapshot \
        --db-cluster-identifier "univesp-polos-${ambiente}-restaurado" \
        --snapshot-identifier $id_snapshot \
        --engine aurora-mysql \
        --region $AWS_DEFAULT_REGION
    
    echo "Restauração iniciada para o snapshot $id_snapshot"
}

# Script para listar backups disponíveis
listar_backups() {
    local ambiente=$1
    
    # Obter ID do cluster Aurora
    local id_cluster=$(aws rds describe-db-clusters \
        --query "DBClusters[?starts_with(DBClusterIdentifier, 'univesp-polos-${ambiente}')].DBClusterIdentifier" \
        --output text)
    
    if [ -z "$id_cluster" ]; then
        echo "Erro: Cluster não encontrado para o ambiente ${ambiente}"
        return 1
    fi
    
    # Listar snapshots
    aws rds describe-db-cluster-snapshots \
        --db-cluster-identifier $id_cluster \
        --query 'DBClusterSnapshots[].{ID:DBClusterSnapshotIdentifier,Criado:SnapshotCreateTime,Status:Status}' \
        --output table
}
