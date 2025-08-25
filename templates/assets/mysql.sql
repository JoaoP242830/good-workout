-- Tabela de usuários
CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    senha VARCHAR(255) NOT NULL,
    tipo ENUM('aluno', 'instrutor', 'admin') DEFAULT 'aluno',
    data_nascimento DATE,
    genero ENUM('masculino', 'feminino', 'outro', 'nao_informar'),
    altura INT, -- em cm
    telefone VARCHAR(20),
    endereco TEXT,
    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP,
    ultimo_login DATETIME,
    ativo TINYINT(1) DEFAULT 1,
    foto VARCHAR(255),
    objetivo ENUM('perda_peso', 'ganho_massa', 'condicionamento', 'outro'),
    observacoes TEXT
);

-- Tabela de exercícios
CREATE TABLE exercicios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    categoria ENUM('peito', 'costas', 'pernas', 'ombros', 'biceps', 'triceps', 'abdomen', 'cardio', 'alongamento') NOT NULL,
    descricao TEXT,
    instrucoes TEXT,
    dicas TEXT,
    equipamento VARCHAR(255),
    dificuldade ENUM('iniciante', 'intermediario', 'avancado'),
    imagem VARCHAR(255),
    video VARCHAR(255),
    musculos_envolvidos TEXT,
    variacoes TEXT,
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    criado_por INT,
    ativo TINYINT(1) DEFAULT 1,
    FOREIGN KEY (criado_por) REFERENCES usuarios(id) ON DELETE SET NULL
);

-- Tabela de planos de treino
CREATE TABLE planos_treino (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(255) NOT NULL,
    descricao TEXT,
    duracao_semanas INT,
    objetivo ENUM('forca', 'hipertrofia', 'resistencia', 'perda_peso', 'condicionamento', 'reabilitacao'),
    nivel ENUM('iniciante', 'intermediario', 'avancado'),
    criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
    criado_por INT,
    publico TINYINT(1) DEFAULT 0,
    ativo TINYINT(1) DEFAULT 1,
    FOREIGN KEY (criado_por) REFERENCES usuarios(id) ON DELETE SET NULL
);

-- Tabela de dias de treino no plano
CREATE TABLE dias_treino (
    id INT AUTO_INCREMENT PRIMARY KEY,
    plano_id INT NOT NULL,
    dia_semana ENUM('segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo'),
    nome VARCHAR(255),
    descricao TEXT,
    ordem INT,
    duracao_estimada INT, -- em minutos
    FOREIGN KEY (plano_id) REFERENCES planos_treino(id) ON DELETE CASCADE
);

-- Tabela de exercícios em cada dia de treino
CREATE TABLE exercicios_dia (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dia_id INT NOT NULL,
    exercicio_id INT NOT NULL,
    series INT,
    repeticoes VARCHAR(20), -- pode ser um intervalo como "8-12"
    carga VARCHAR(50),
    descanso VARCHAR(20), -- tempo entre séries em segundos
    observacoes TEXT,
    ordem INT,
    FOREIGN KEY (dia_id) REFERENCES dias_treino(id) ON DELETE CASCADE,
    FOREIGN KEY (exercicio_id) REFERENCES exercicios(id) ON DELETE CASCADE
);

-- Tabela de usuários atribuídos a planos
CREATE TABLE usuario_planos (
    usuario_id INT NOT NULL,
    plano_id INT NOT NULL,
    data_inicio DATE NOT NULL,
    data_fim DATE,
    ativo TINYINT(1) DEFAULT 1,
    PRIMARY KEY (usuario_id, plano_id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (plano_id) REFERENCES planos_treino(id) ON DELETE CASCADE
);

-- Tabela de histórico de treinos realizados
CREATE TABLE historico_treinos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    dia_id INT,
    data DATE NOT NULL,
    hora_inicio TIME,
    hora_fim TIME,
    duracao INT, -- em minutos
    percepcao_esforco INT CHECK (percepcao_esforco BETWEEN 1 AND 10),
    observacoes TEXT,
    completo TINYINT(1) DEFAULT 1,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (dia_id) REFERENCES dias_treino(id) ON DELETE SET NULL
);

-- Tabela de exercícios realizados em cada treino
CREATE TABLE exercicios_realizados (
    id INT AUTO_INCREMENT PRIMARY KEY,
    treino_id INT NOT NULL,
    exercicio_id INT NOT NULL,
    exercicio_dia_id INT,
    series_completas INT,
    repeticoes_por_serie VARCHAR(20),
    carga_utilizada VARCHAR(50),
    observacoes TEXT,
    FOREIGN KEY (treino_id) REFERENCES historico_treinos(id) ON DELETE CASCADE,
    FOREIGN KEY (exercicio_id) REFERENCES exercicios(id) ON DELETE CASCADE,
    FOREIGN KEY (exercicio_dia_id) REFERENCES exercicios_dia(id) ON DELETE SET NULL
);

-- Tabela de medidas corporais
CREATE TABLE medidas_corporais (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    data DATE NOT NULL,
    peso DECIMAL(5,2), -- em kg
    altura INT, -- em cm
    gordura_corporal DECIMAL(5,2), -- porcentagem
    massa_muscular DECIMAL(5,2), -- porcentagem
    circunferencia_peito DECIMAL(5,2), -- em cm
    circunferencia_cintura DECIMAL(5,2),
    circunferencia_quadril DECIMAL(5,2),
    circunferencia_braco_esquerdo DECIMAL(5,2),
    circunferencia_braco_direito DECIMAL(5,2),
    circunferencia_coxa_esquerda DECIMAL(5,2),
    circunferencia_coxa_direita DECIMAL(5,2),
    circunferencia_panturrilha_esquerda DECIMAL(5,2),
    circunferencia_panturrilha_direita DECIMAL(5,2),
    observacoes TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabela de avaliações físicas
CREATE TABLE avaliacoes_fisicas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    instrutor_id INT,
    data DATE NOT NULL,
    peso DECIMAL(5,2),
    altura INT,
    imc DECIMAL(5,2),
    gordura_corporal DECIMAL(5,2),
    massa_muscular DECIMAL(5,2),
    flexibilidade ENUM('ruim', 'regular', 'boa', 'otima'),
    resistencia ENUM('ruim', 'regular', 'boa', 'otima'),
    forca ENUM('ruim', 'regular', 'boa', 'otima'),
    observacoes TEXT,
    recomendacoes TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (instrutor_id) REFERENCES usuarios(id) ON DELETE SET NULL
);

-- Tabela de pagamentos
CREATE TABLE pagamentos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    valor DECIMAL(10,2) NOT NULL,
    data_pagamento DATE NOT NULL,
    metodo ENUM('dinheiro', 'cartao_credito', 'cartao_debito', 'pix', 'transferencia'),
    mes_referencia CHAR(7) NOT NULL, -- formato YYYY-MM
    status ENUM('pendente', 'pago', 'atrasado', 'cancelado'),
    observacoes TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabela de mensagens
CREATE TABLE mensagens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    remetente_id INT NOT NULL,
    destinatario_id INT NOT NULL,
    assunto VARCHAR(255),
    mensagem TEXT NOT NULL,
    data_envio DATETIME DEFAULT CURRENT_TIMESTAMP,
    lida TINYINT(1) DEFAULT 0,
    respondida TINYINT(1) DEFAULT 0,
    FOREIGN KEY (remetente_id) REFERENCES usuarios(id) ON DELETE CASCADE,
    FOREIGN KEY (destinatario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabela de notificações
CREATE TABLE notificacoes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT NOT NULL,
    titulo VARCHAR(255) NOT NULL,
    mensagem TEXT NOT NULL,
    tipo ENUM('info', 'alerta', 'lembrete', 'atualizacao'),
    data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP,
    lida TINYINT(1) DEFAULT 0,
    link VARCHAR(255),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- Tabela de configurações do sistema
CREATE TABLE configuracoes (
    chave VARCHAR(255) PRIMARY KEY,
    valor TEXT,
    descricao TEXT,
    tipo ENUM('string', 'numero', 'booleano', 'json')
);

-- Tabela de logs de atividades (corrigido o nome da tabela)
CREATE TABLE logs_atividade (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    acao VARCHAR(255) NOT NULL,
    tabela_afetada VARCHAR(255),
    id_registro INT,
    dados_anteriores TEXT,
    dados_novos TEXT,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
    ip VARCHAR(45),
    user_agent TEXT,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE SET NULL
);