-- Script de criação do banco de dados para o sistema UNIVESP Polos
-- Compatível com MySQL 8+ e Aurora MySQL

-- Criação do banco de dados
CREATE DATABASE IF NOT EXISTS univesp_polos
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE univesp_polos;

-- Tabela de usuários (auth_user)
CREATE TABLE auth_user (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME NULL,
    is_superuser BOOLEAN NOT NULL DEFAULT FALSE,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN NOT NULL DEFAULT FALSE,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    date_joined DATETIME NOT NULL,
    aws_iam_user_id VARCHAR(255) NULL,
    aws_iam_role VARCHAR(255) NULL,
    last_aws_sync DATETIME NULL,
    is_local_only BOOLEAN NOT NULL DEFAULT TRUE,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB;

-- Tabela de grupos
CREATE TABLE auth_group (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Tabela de permissões
CREATE TABLE auth_permission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id INT NOT NULL,
    codename VARCHAR(100) NOT NULL,
    UNIQUE KEY unique_content_type_codename (content_type_id, codename)
) ENGINE=InnoDB;

-- Tabela de associação usuário-grupo
CREATE TABLE auth_user_groups (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    group_id INT NOT NULL,
    UNIQUE KEY unique_user_group (user_id, group_id),
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (group_id) REFERENCES auth_group(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Tabela de associação usuário-permissões
CREATE TABLE auth_user_user_permissions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    permission_id INT NOT NULL,
    UNIQUE KEY unique_user_permission (user_id, permission_id),
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES auth_permission(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Tabela de polos
CREATE TABLE polos_polo (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    cep VARCHAR(9) NOT NULL,
    endereco VARCHAR(255) NOT NULL,
    numero VARCHAR(20) NOT NULL,
    complemento VARCHAR(100) NULL,
    bairro VARCHAR(100) NOT NULL,
    cidade VARCHAR(100) NOT NULL,
    estado VARCHAR(2) NOT NULL,
    latitude DECIMAL(10,8) NULL,
    longitude DECIMAL(11,8) NULL,
    telefone VARCHAR(20) NOT NULL,
    email VARCHAR(254) NOT NULL,
    cursos_oferecidos TEXT NOT NULL,
    horario_atendimento TEXT NOT NULL,
    atividades_extras TEXT NULL,
    atividades_esportivas TEXT NULL,
    data_cadastro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ultima_atualizacao DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_cidade_estado (cidade, estado),
    INDEX idx_cep (cep)
) ENGINE=InnoDB;

-- Tabela de feedback
CREATE TABLE polos_userfeedback (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    email VARCHAR(254) NOT NULL,
    telefone VARCHAR(20) NULL,
    tipo_feedback VARCHAR(20) NOT NULL,
    mensagem TEXT NOT NULL,
    pagina_origem VARCHAR(255) NOT NULL,
    data_envio DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'pendente',
    resposta TEXT NULL,
    data_resposta DATETIME NULL,
    INDEX idx_status (status),
    INDEX idx_data_envio (data_envio),
    INDEX idx_tipo_feedback (tipo_feedback)
) ENGINE=InnoDB;

-- Tabelas para sessões do Django
CREATE TABLE django_session (
    session_key VARCHAR(40) NOT NULL PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date DATETIME NOT NULL,
    INDEX idx_expire_date (expire_date)
) ENGINE=InnoDB;

-- Tabela para content types do Django
CREATE TABLE django_content_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE KEY unique_app_model (app_label, model)
) ENGINE=InnoDB;

-- Tabela para migrações do Django
CREATE TABLE django_migrations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied DATETIME NOT NULL
) ENGINE=InnoDB;

-- Tabela para log de admin
CREATE TABLE django_admin_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action_time DATETIME NOT NULL,
    object_id TEXT NULL,
    object_repr VARCHAR(200) NOT NULL,
    action_flag SMALLINT UNSIGNED NOT NULL,
    change_message TEXT NOT NULL,
    content_type_id INT NULL,
    user_id BIGINT NOT NULL,
    FOREIGN KEY (content_type_id) REFERENCES django_content_type(id) ON DELETE SET NULL,
    FOREIGN KEY (user_id) REFERENCES auth_user(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Configurações iniciais
INSERT INTO django_content_type (app_label, model) VALUES
    ('admin', 'logentry'),
    ('auth', 'permission'),
    ('auth', 'group'),
    ('contenttypes', 'contenttype'),
    ('sessions', 'session'),
    ('polos', 'polo'),
    ('polos', 'userfeedback'),
    ('polos', 'customuser');

-- Permissões básicas
INSERT INTO auth_permission (name, content_type_id, codename)
SELECT 'Can add polo', id, 'add_polo' FROM django_content_type WHERE app_label = 'polos' AND model = 'polo'
UNION ALL
SELECT 'Can change polo', id, 'change_polo' FROM django_content_type WHERE app_label = 'polos' AND model = 'polo'
UNION ALL
SELECT 'Can delete polo', id, 'delete_polo' FROM django_content_type WHERE app_label = 'polos' AND model = 'polo'
UNION ALL
SELECT 'Can view polo', id, 'view_polo' FROM django_content_type WHERE app_label = 'polos' AND model = 'polo'
UNION ALL
SELECT 'Can add feedback', id, 'add_userfeedback' FROM django_content_type WHERE app_label = 'polos' AND model = 'userfeedback'
UNION ALL
SELECT 'Can change feedback', id, 'change_userfeedback' FROM django_content_type WHERE app_label = 'polos' AND model = 'userfeedback'
UNION ALL
SELECT 'Can delete feedback', id, 'delete_userfeedback' FROM django_content_type WHERE app_label = 'polos' AND model = 'userfeedback'
UNION ALL
SELECT 'Can view feedback', id, 'view_userfeedback' FROM django_content_type WHERE app_label = 'polos' AND model = 'userfeedback';

-- Comentários sobre configurações importantes
/*
Notas sobre o banco de dados:
1. Usar UTF8MB4 para suporte completo a Unicode
2. Índices criados para campos frequentemente pesquisados
3. Chaves estrangeiras com DELETE CASCADE onde apropriado
4. Timestamps automáticos para data_cadastro e ultima_atualizacao
5. Campos de texto usando TEXT para conteúdo longo
6. Valores DEFAULT apropriados definidos
7. Compatível com AWS Aurora MySQL

Requisitos do sistema:
- MySQL 8.0+ ou AWS Aurora MySQL
- Collation: utf8mb4_unicode_ci
- Suporte a InnoDB
- Timezone configurado corretamente

Para usar com AWS Aurora:
1. Criar cluster Aurora MySQL
2. Usar mesmo charset e collation
3. Configurar grupo de segurança apropriado
4. Configurar backup automático
5. Considerar réplicas de leitura para escalabilidade

Comandos úteis:
- Backup: mysqldump -u root -p univesp_polos > backup.sql
- Restore: mysql -u root -p univesp_polos < backup.sql
*/
