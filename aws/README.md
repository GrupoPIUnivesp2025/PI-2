# Documentação da Infraestrutura UNIVESP Polos

## Visão Geral

Esta documentação descreve a infraestrutura AWS da aplicação UNIVESP Polos, incluindo todos os componentes, scripts de gerenciamento e procedimentos operacionais.

## Componentes da Infraestrutura

### 1. Rede (network.yaml)

- VPC dedicada
- Subredes públicas e privadas em duas zonas de disponibilidade
- NAT Gateways para acesso à internet das subredes privadas
- Grupos de segurança para controle de acesso

### 2. Banco de Dados (database.yaml)

- Cluster Aurora MySQL
- Configuração multi-AZ para alta disponibilidade em produção
- Backup automatizado
- Parâmetros otimizados para a aplicação

### 3. Aplicação (application.yaml)

- Cluster ECS Fargate
- Balanceador de carga com SSL/TLS
- Auto scaling baseado em CPU
- Integração com CloudWatch Logs

### 4. Arquivos Estáticos (static_assets.yaml)

- Bucket S3 para armazenamento
- CloudFront CDN para distribuição
- Certificado SSL/TLS
- Configuração de CORS e cache

### 5. Monitoramento (monitoring.yaml)

- Dashboard CloudWatch
- Alarmes para CPU, memória e erros
- Sistema de backup automatizado
- Notificações por email

## Scripts de Gerenciamento

### 1. deploy.sh

Script principal para implantação da infraestrutura completa:

```bash
./deploy.sh [ambiente]  # ambiente: prod ou staging
```

### 2. update.sh

Script para atualização da aplicação sem downtime:

```bash
./update.sh [ambiente]  # ambiente: prod ou staging
```

### 3. backup_utils.sh

Utilitários para gerenciamento de backups:

```bash
# Criar backup manual
./backup_utils.sh [ambiente] criar

# Restaurar backup
./backup_utils.sh [ambiente] restaurar [id_snapshot]

# Listar backups disponíveis
./backup_utils.sh [ambiente] listar
```

## Pipeline de CI/CD

### Fluxo de Trabalho

1. Push para branches principais (main/staging)
2. Execução automática de testes
3. Build da imagem Docker
4. Push para Amazon ECR
5. Deploy automático para ambiente apropriado

### Ambientes de Deploy

- Staging: Atualizado automaticamente com pushes para branch staging
- Produção: Atualizado automaticamente com pushes para branch main

### Verificações de Segurança e Qualidade

- Testes automatizados
- Análise de dependências
- Verificação de credenciais
- Validação de configurações
- Análise SonarQube
- Verificação de segurança com Bandit
- Monitoramento de performance com New Relic

### Sistema de Rollback

- Detecção automática de falhas
- Rollback automático para última versão estável
- Notificação da equipe via SNS
- Validação pós-rollback
- Logs detalhados do processo

## Procedimentos Operacionais

### Implantação Inicial

1. Configurar variáveis de ambiente AWS
2. Executar deploy.sh para criar toda a infraestrutura
3. Validar recursos criados no console AWS
4. Verificar endpoints e DNS

### Atualizações da Aplicação

1. Fazer commit das alterações
2. Executar update.sh para implantar as mudanças
3. Monitorar logs durante a atualização
4. Verificar status da aplicação

### Backup e Restauração

1. Backups automáticos diários e semanais
2. Backups manuais via backup_utils.sh
3. Procedimento de restauração documentado
4. Testes regulares de restauração

### Monitoramento

1. Dashboard CloudWatch centralizado
2. Alertas configurados para:
   - Alta utilização de CPU
   - Problemas de memória
   - Erros HTTP 5xx
   - Falhas de backup
3. Logs centralizados no CloudWatch

## Ambientes

### Produção

- Multi-AZ para alta disponibilidade
- Backup retido por 30 dias
- SSL/TLS obrigatório
- Escalabilidade automática

### Staging

- Single-AZ para redução de custos
- Backup retido por 7 dias
- Ambiente para testes
- Recursos reduzidos

## Segurança

### Rede

- VPC isolada
- Subredes privadas para recursos críticos
- Security groups restritivos
- SSL/TLS em todas as conexões

### Dados

- Criptografia em repouso
- Backups criptografados
- Acesso restrito por IAM
- Monitoramento de segurança

### Conformidade

- Logs de auditoria
- Monitoramento de alterações
- Backup e recuperação
- Controle de acesso

## Resolução de Problemas

### Problemas Comuns

1. Falha na implantação

   - Verificar logs do CloudFormation
   - Validar permissões IAM
   - Verificar limites de serviço

2. Problemas de conexão

   - Verificar security groups
   - Validar configurações de rede
   - Testar conectividade

3. Erros na aplicação
   - Consultar logs no CloudWatch
   - Verificar métricas de recursos
   - Validar configurações

### Contatos de Suporte

- Time de Infraestrutura
- Time de Desenvolvimento
- Suporte AWS

## Manutenção

### Rotinas Diárias

- Monitorar alertas
- Verificar logs
- Validar backups

### Manutenção Mensal

- Revisar métricas
- Atualizar patches
- Testar recuperação
- Revisar custos

### Manutenção Trimestral

- Teste de recuperação de desastres
- Revisão de segurança
- Otimização de recursos
- Atualização de documentação
