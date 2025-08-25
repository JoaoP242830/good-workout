#!/usr/bin/env python3
"""
Script de inicialização do banco de dados para o Sistema Academia Fitness
Execute este script antes de rodar o app.py pela primeira vez
"""

import mysql.connector
from mysql.connector import Error
from werkzeug.security import generate_password_hash
import os

def init_database():
    try:
        print("🚀 Iniciando configuração do banco de dados...")
        
        # Conectar ao MySQL Server (sem especificar o banco ainda)
        conn = mysql.connector.connect(
            host='localhost',
            user='root',
            password='200825Jp!'  # Altere se sua senha do MySQL for diferente
        )
        
        cursor = conn.cursor()
        
        # 1. Criar banco de dados se não existir
        print("📋 Criando banco de dados 'academia'...")
        cursor.execute("CREATE DATABASE IF NOT EXISTS academia")
        cursor.execute("USE academia")
        
        # 2. Criar tabelas
        print("📊 Criando tabelas...")
        
        # Tabela de usuários
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                senha VARCHAR(255) NOT NULL,
                tipo VARCHAR(50) DEFAULT 'aluno',
                data_nascimento DATE,
                genero VARCHAR(20),
                altura INT,
                objetivo TEXT,
                bio TEXT,
                data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de exercícios
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercicios (
                id INT AUTO_INCREMENT PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                categoria VARCHAR(100) NOT NULL,
                descricao TEXT,
                instrucoes TEXT,
                dicas TEXT,
                series VARCHAR(100),
                imagem VARCHAR(255),
                criado_em DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de planos de treino
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS planos_treino (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT,
                nome VARCHAR(255) NOT NULL,
                duracao INT,
                objetivo TEXT,
                dificuldade VARCHAR(100),
                descricao TEXT,
                criado_em DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
            )
        ''')
        
        # Tabela de dias de treino
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dias_treino (
                id INT AUTO_INCREMENT PRIMARY KEY,
                plano_id INT,
                dia_semana VARCHAR(20),
                descricao TEXT,
                FOREIGN KEY (plano_id) REFERENCES planos_treino (id) ON DELETE CASCADE
            )
        ''')
        
        # Tabela de exercícios do treino
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS exercicios_treino (
                id INT AUTO_INCREMENT PRIMARY KEY,
                dia_id INT,
                exercicio_id INT,
                series VARCHAR(100),
                repeticoes VARCHAR(100),
                descricao TEXT,
                FOREIGN KEY (dia_id) REFERENCES dias_treino (id) ON DELETE CASCADE,
                FOREIGN KEY (exercicio_id) REFERENCES exercicios (id) ON DELETE CASCADE
            )
        ''')
        
        # Tabela de medidas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medidas (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT,
                data DATE NOT NULL,
                peso DECIMAL(5,2),
                gordura_corporal DECIMAL(5,2),
                massa_muscular DECIMAL(5,2),
                peito DECIMAL(5,2),
                cintura DECIMAL(5,2),
                quadril DECIMAL(5,2),
                braco DECIMAL(5,2),
                coxa DECIMAL(5,2),
                panturrilha DECIMAL(5,2),
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
            )
        ''')
        
        # Tabela de histórico de treinos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS historico_treinos (
                id INT AUTO_INCREMENT PRIMARY KEY,
                usuario_id INT,
                data DATETIME NOT NULL,
                tipo_treino VARCHAR(100),
                duracao VARCHAR(50),
                calorias INT,
                observacoes TEXT,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id) ON DELETE CASCADE
            )
        ''')
        
        # 3. Inserir dados iniciais
        print("👤 Criando usuário administrador...")
        
        # Verificar se o usuário admin já existe
        cursor.execute("SELECT * FROM usuarios WHERE email = 'admin@academia.com'")
        if not cursor.fetchone():
            senha_hash = generate_password_hash('admin123')
            cursor.execute(
                "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (%s, %s, %s, %s)",
                ('Administrador', 'admin@academia.com', senha_hash, 'admin')
            )
            print("✅ Usuário admin criado: admin@academia.com / admin123")
        else:
            print("⚠️  Usuário admin já existe")
        
        # Inserir exercícios de exemplo
        print("💪 Inserindo exercícios de exemplo...")
        cursor.execute("SELECT COUNT(*) FROM exercicios")
        count = cursor.fetchone()[0]
        
        if count == 0:
            sample_exercises = [
                {
                    'nome': 'Supino Reto com Barra',
                    'categoria': 'peito',
                    'descricao': 'Exercício fundamental para desenvolvimento do peitoral maior, deltoides anterior e tríceps.',
                    'instrucoes': 'Deite-se no banco com os pés apoiados no chão. Segure a barra com as mãos um pouco além da largura dos ombros. Desça a barra até o peito e empurre para cima até estender os braços.',
                    'dicas': 'Mantenha as escápulas retraídas e não arqueie excessivamente as costas.',
                    'series': '3-4 séries de 8-12 repetições',
                    'imagem': 'supino_reto.gif'
                },
                {
                    'nome': 'Agachamento Livre',
                    'categoria': 'pernas',
                    'descricao': 'Exercício completo para quadríceps, glúteos e posterior de coxa, considerado o rei dos exercícios.',
                    'instrucoes': 'Posicione os pés na largura dos ombros. Desça flexionando os joelhos e quadril, mantendo o peito erguido. Desça até as coxas ficarem paralelas ao chão e retorne.',
                    'dicas': 'Mantenha o peso nos calcanhares e não deixe os joelhos passarem dos dedos dos pés.',
                    'series': '4 séries de 6-10 repetições',
                    'imagem': 'agachamento_livre.gif'
                },
                {
                    'nome': 'Barra Fixa',
                    'categoria': 'costas',
                    'descricao': 'Excelente exercício para desenvolvimento das costas, especialmente o latíssimo do dorso.',
                    'instrucoes': 'Segure a barra com as mãos na largura dos ombros (pegada pronada). Puxe o corpo para cima até o queixo passar a barra. Desça controladamente.',
                    'dicas': 'Mantenha o core ativado e evite balançar o corpo para ajudar no movimento.',
                    'series': '3-4 séries até a falha',
                    'imagem': 'barra_fixa.gif'
                },
                {
                    'nome': 'Rosca Direta com Barra',
                    'categoria': 'biceps',
                    'descricao': 'Exercício clássico para isolamento do bíceps braquial.',
                    'instrucoes': 'Em pé, segure a barra com as mãos na largura dos ombros (pegada supinada). Flexione os cotovelos levando a barra até os ombros. Desça controladamente.',
                    'dicas': 'Mantenha os cotovelos fixos ao lado do corpo e evite usar impulso.',
                    'series': '3-4 séries de 10-12 repetições',
                    'imagem': 'rosca_direta.gif'
                },
                {
                    'nome': 'Tríceps Corda',
                    'categoria': 'triceps',
                    'descricao': 'Exercício eficiente para trabalhar as três porções do tríceps.',
                    'instrucoes': 'Segure a corda com as mãos na altura do peito. Empurre para baixo até estender completamente os braços. Volte controladamente.',
                    'dicas': 'Mantenha os cotovelos fixos e o corpo ereto, sem inclinar para frente.',
                    'series': '3 séries de 12-15 repetições',
                    'imagem': 'triceps_corda.gif'
                },
                {
                    'nome': 'Desenvolvimento Militar',
                    'categoria': 'ombros',
                    'descricao': 'Exercício fundamental para desenvolvimento dos deltoides (ombros).',
                    'instrucoes': 'Sentado ou em pé, segure a barra na altura dos ombros. Empurre para cima até estender os braços. Desça controladamente.',
                    'dicas': 'Mantenha o core ativado e não arqueie excessivamente as costas.',
                    'series': '3-4 séries de 8-10 repetições',
                    'imagem': 'desenvolvimento_militar.gif'
                },
                {
                    'nome': 'Prancha Frontal',
                    'categoria': 'abdomen',
                    'descricao': 'Exercício isométrico excelente para fortalecimento do core.',
                    'instrucoes': 'Apoie os antebraços no chão com os cotovelos alinhados aos ombros. Mantenha o corpo reto, apoiado nas pontas dos pés. Contraia o abdômen.',
                    'dicas': 'Não deixe o quadril cair ou subir demais. Mantenha a coluna neutra.',
                    'series': '3-4 séries de 30-60 segundos',
                    'imagem': 'prancha.png'
                },
                {
                    'nome': 'Exercícios de Impulsão',
                    'categoria': 'basquete',
                    'descricao': 'Treinos focados no salto vertical e potência nas pernas.',
                    'instrucoes': 'Realize saltos pliométricos, agachamentos com salto e saltos contínuos para desenvolver explosão.',
                    'dicas': 'Mantenha a postura correta e foque em saltos rápidos e explosivos.',
                    'series': '3-4 séries de 12-15 repetições',
                    'imagem': 'impulsao.gif'
                },
                {
                    'nome': 'Saque',
                    'categoria': 'volei',
                    'descricao': 'Ação inicial da jogada no vôlei.',
                    'instrucoes': 'Segure a bola com uma mão, lance-a levemente e golpeie com a outra.',
                    'dicas': 'Varie entre saque flutuante e viagem para treinar diferentes estilos.',
                    'series': '4 séries de 10 saques',
                    'imagem': 'saque.gif'
                },
                {
                    'nome': 'Chute',
                    'categoria': 'futebol',
                    'descricao': 'Movimento principal para finalizar jogadas.',
                    'instrucoes': 'Apoie o pé de base ao lado da bola e chute com a parte do pé desejada.',
                    'dicas': 'Mantenha o corpo levemente inclinado sobre a bola para evitar chutes altos.',
                    'series': '4 séries de 8-12 chutes',
                    'imagem': 'chute.gif'
                },
                {
                    'nome': 'Crucifixo com Halteres',
                    'categoria': 'peito',
                    'descricao': 'Exercício de isolamento para o peitoral, especialmente as porções esternais.',
                    'instrucoes': 'Deitado no banco, segure os halteres com os braços estendidos acima do peito. Abra os braços em um arco até os halteres ficarem na altura do peito. Retorne à posição inicial.',
                    'dicas': 'Mantenha uma leve flexão nos cotovelos e controle o movimento em toda amplitude.',
                    'series': '3 séries de 12-15 repetições',
                    'imagem': 'Crucifixo_inclinado.gif'
                },
                {
                    'nome': 'Remada Curvada',
                    'categoria': 'costas',
                    'descricao': 'Exercício excelente para desenvolvimento dos músculos das costas.',
                    'instrucoes': 'Com os pés na largura dos ombros e joelhos levemente flexionados, incline o tronco para frente. Puxe a barra em direção ao abdômen, mantendo os cotovelos próximos ao corpo.',
                    'dicas': 'Mantenha as costas retas e contraia as escápulas no topo do movimento.',
                    'series': '3-4 séries de 8-10 repetições',
                    'imagem': 'Remada_curvada.gif'
                },
                {
                    'nome': 'Leg Press 45°',
                    'categoria': 'pernas',
                    'descricao': 'Exercício eficiente para quadríceps, gluteos e posterior de coxa.',
                    'instrucoes': 'Sente-se no aparelho com os pés na plataforma na largura dos ombros. Empurre a plataforma até quase estender as pernas. Desça controladamente.',
                    'dicas': 'Não trave os joelhos no topo do movimento e mantenha os pés alinhados com os joelhos.',
                    'series': '3-4 séries de 10-12 repetições',
                    'imagem': 'Press_45.gif'
                }
            ]
            
            for exercise in sample_exercises:
                cursor.execute(
                    '''INSERT INTO exercicios 
                    (nome, categoria, descricao, instrucoes, dicas, series, imagem) 
                    VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                    (exercise['nome'], exercise['categoria'], exercise['descricao'],
                     exercise['instrucoes'], exercise['dicas'], exercise['series'], exercise['imagem'])
                )
            
            print(f"✅ {len(sample_exercises)} exercícios inseridos")
        else:
            print("⚠️  Exercícios já existem no banco")
        
        # Criar pastas para uploads se não existirem
        print("📁 Criando diretórios para uploads...")
        os.makedirs('static/uploads', exist_ok=True)
        os.makedirs('static/assets', exist_ok=True)
        
        conn.commit()
        print("🎉 Banco de dados inicializado com sucesso!")
        print("\n📋 Resumo:")
        print("   - Banco de dados: academia")
        print("   - Tabelas criadas: usuarios, exercicios, planos_treino, dias_treino, exercicios_treino, medidas, historico_treinos")
        print("   - Usuário admin: admin@academia.com / admin123")
        print("   - Exercícios inseridos: 13")
        print("\n▶️  Agora execute: python app.py")
        
    except Error as e:
        print(f"❌ Erro ao inicializar banco de dados: {e}")
        print("\n💡 Solução de problemas:")
        print("   - Verifique se o MySQL está instalado e rodando")
        print("   - Confirme se a senha do MySQL está correta")
        print("   - Execute o MySQL como administrador se necessário")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("\n🔌 Conexão com o MySQL fechada")

if __name__ == "__main__":
    print("=" * 50)
    print("INICIALIZADOR DO BANCO DE DADOS - ACADEMIA FITNESS")
    print("=" * 50)
    
    init_database()