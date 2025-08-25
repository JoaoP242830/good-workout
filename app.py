from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import json
from flask import jsonify

app = Flask(__name__)
app.secret_key = 'sua_chave_secreta_super_segura_aqui_123!'
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = '200825Jp!'
app.config['MYSQL_DB'] = 'academia'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['EXERCISE_IMAGES'] = 'static/assets'

# Ensure upload folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['EXERCISE_IMAGES'], exist_ok=True)

# Database functions
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        return conn
    except Error as e:
        print(f"Erro ao conectar ao MySQL: {e}")
        return None


# Helper functions
def calculate_imc(peso, altura):
    if peso and altura:
        return peso / ((altura / 100) ** 2)
    return None

def get_imc_classification(imc):
    if imc < 18.5:
        return "Abaixo do peso"
    elif imc < 25:
        return "Peso normal"
    elif imc < 30:
        return "Sobrepeso"
    else:
        return "Obesidade"

def get_user_data(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM usuarios WHERE id = %s', (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def get_last_measurement(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT * FROM medidas WHERE usuario_id = %s ORDER BY data DESC LIMIT 1',
        (user_id,)
    )
    measurement = cursor.fetchone()
    cursor.close()
    conn.close()
    return measurement

# Routes
@app.route("/")
def index():
    return render_template("login.html")
    

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    senha = request.form.get('senha')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM usuarios WHERE email = %s', (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if user and check_password_hash(user['senha'], senha):
        session['usuario_id'] = user['id']
        session['usuario_nome'] = user['nome']
        session['usuario_tipo'] = user['tipo']
        
        # Store user data in session
        user_data = {
            'id': user['id'],
            'nome': user['nome'],
            'email': user['email'],
            'tipo': user['tipo'],
            'data_nascimento': user['data_nascimento'],
            'genero': user['genero'],
            'altura': user['altura'],
            'objetivo': user['objetivo'],
            'bio': user['bio']
        }
        session['user_data'] = user_data
        
        return jsonify({'success': True, 'redirect': url_for('painel')})
    else:
        return jsonify({'success': False, 'message': 'E-mail ou senha incorretos'})

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')
    confirmar_senha = request.form.get('confirmar_senha')
    
    if senha != confirmar_senha:
        return jsonify({'success': False, 'message': 'As senhas não coincidem'})
    
    try:
        senha_hash = generate_password_hash(senha)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO usuarios (nome, email, senha) VALUES (%s, %s, %s)',
            (nome, email, senha_hash)
        )
        user_id = cursor.lastrowid
        conn.commit()
        cursor.close()
        conn.close()
        
        # Set session
        session['usuario_id'] = user_id
        session['usuario_nome'] = nome
        session['usuario_tipo'] = 'aluno'
        
        return jsonify({'success': True, 'redirect': url_for('painel')})
    except Error as e:
        if "Duplicate entry" in str(e):
            return jsonify({'success': False, 'message': 'E-mail já cadastrado'})
        return jsonify({'success': False, 'message': str(e)})

@app.route('/painel')
def painel():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))   
    
    user_id = session['usuario_id']
    user = get_user_data(user_id)
    last_measurement = get_last_measurement(user_id)
    
    # Calculate IMC if possible
    imc = None
    imc_class = None
    if last_measurement and last_measurement['peso'] and user['altura']:
        imc = calculate_imc(last_measurement['peso'], user['altura'])
        imc_class = get_imc_classification(imc)
    
    # Get workout history (last 5 workouts)
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT * FROM historico_treinos WHERE usuario_id = %s ORDER BY data DESC LIMIT 5',
        (user_id,)
    )
    workouts = cursor.fetchall()
    
    # Get upcoming workouts (next 3 days)
    today = datetime.now().date()
    end_date = today + timedelta(days=3)
    
    cursor.execute(
        '''SELECT * FROM historico_treinos 
        WHERE usuario_id = %s AND date(data) BETWEEN date(%s) AND date(%s)
        ORDER BY data''',
        (user_id, today, end_date)
    )
    upcoming_workouts = cursor.fetchall()
    
    # Get exercise categories for the exercise section
    cursor.execute(
        'SELECT DISTINCT categoria FROM exercicios ORDER BY categoria'
    )
    categories = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('painel.html', 
                         user=user,
                         last_measurement=last_measurement,
                         imc=imc,
                         imc_class=imc_class,
                         workouts=workouts,
                         upcoming_workouts=upcoming_workouts,
                         categories=categories)

@app.route('/exercicios')
def exercicios():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))
    
    categoria = request.args.get('categoria', 'all')
    search = request.args.get('search', '')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    query = 'SELECT * FROM exercicios'
    params = []
    
    if categoria != 'all' or search:
        conditions = []
        if categoria != 'all':
            conditions.append('categoria = %s')
            params.append(categoria)
        if search:
            conditions.append('(nome LIKE %s OR descricao LIKE %s OR instrucoes LIKE %s)')
            params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
        
        query += ' WHERE ' + ' AND '.join(conditions)
    
    query += ' ORDER BY nome'
    cursor.execute(query, params)
    exercicios = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return jsonify(exercicios)

@app.route('/exercicio/<int:exercise_id>')
def exercicio(exercise_id):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        'SELECT * FROM exercicios WHERE id = %s',
        (exercise_id,)
    )
    exercise = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if exercise:
        return jsonify(exercise)
    else:
        return jsonify({'error': 'Exercício não encontrado'}), 404

@app.route('/perfil/salvar', methods=['POST'])
def salvar_perfil():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))
    
    user_id = session['usuario_id']
    data = request.get_json()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''UPDATE usuarios SET 
            nome = %s, 
            data_nascimento = %s, 
            genero = %s, 
            altura = %s, 
            objetivo = %s, 
            bio = %s 
            WHERE id = %s''',
            (data['nome'], data['data_nascimento'], data['genero'], 
             data['altura'], data['objetivo'], data['bio'], user_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        # Update session data
        session['usuario_nome'] = data['nome']
        if 'user_data' in session:
            session['user_data'].update({
                'nome': data['nome'],
                'data_nascimento': data['data_nascimento'],
                'genero': data['genero'],
                'altura': data['altura'],
                'objetivo': data['objetivo'],
                'bio': data['bio']
            })
        
        return jsonify({'success': True, 'message': 'Perfil atualizado com sucesso'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/medidas/salvar', methods=['POST'])
def salvar_medidas():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))
    
    user_id = session['usuario_id']
    data = request.get_json()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO medidas 
            (usuario_id, data, peso, gordura_corporal, massa_muscular, 
             peito, cintura, quadril, braco, coxa, panturrilha)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
            (user_id, data['data'], data['peso'], data['gordura_corporal'], 
             data['massa_muscular'], data['peito'], data['cintura'], 
             data['quadril'], data['braco'], data['coxa'], data['panturrilha'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Medidas salvas com sucesso'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/medidas/historico')
def historico_medidas():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))
    
    user_id = session['usuario_id']
    periodo = request.args.get('periodo', '1m')
    
    # Calculate date range based on period
    end_date = datetime.now().date()
    if periodo == '1m':
        start_date = end_date - timedelta(days=30)
    elif periodo == '3m':
        start_date = end_date - timedelta(days=90)
    elif periodo == '6m':
        start_date = end_date - timedelta(days=180)
    elif periodo == '1y':
        start_date = end_date - timedelta(days=365)
    else:  # all
        start_date = None
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    if start_date:
        cursor.execute(
            '''SELECT * FROM medidas 
            WHERE usuario_id = %s AND date(data) BETWEEN date(%s) AND date(%s)
            ORDER BY data''',
            (user_id, start_date, end_date)
        )
    else:
        cursor.execute(
            'SELECT * FROM medidas WHERE usuario_id = %s ORDER BY data',
            (user_id,)
        )
    
    medidas = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return jsonify(medidas)

@app.route('/treinos/plano/novo', methods=['POST'])
def novo_plano_treino():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))
    
    user_id = session['usuario_id']
    data = request.get_json()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert workout plan
        cursor.execute(
            '''INSERT INTO planos_treino 
            (usuario_id, nome, duracao, objetivo, dificuldade, descricao)
            VALUES (%s, %s, %s, %s, %s, %s)''',
            (user_id, data['nome'], data['duracao'], data['objetivo'], 
             data['dificuldade'], data['descricao'])
        )
        plano_id = cursor.lastrowid
        
        # Insert workout days
        for dia in data['dias']:
            cursor.execute(
                '''INSERT INTO dias_treino 
                (plano_id, dia_semana, descricao)
                VALUES (%s, %s, %s)''',
                (plano_id, dia['dia_semana'], dia['descricao'])
            )
            dia_id = cursor.lastrowid
            
            # Insert exercises for each day
            for exercicio in dia['exercicios']:
                cursor.execute(
                    '''INSERT INTO exercicios_treino 
                    (dia_id, exercicio_id, series, repeticoes, descricao)
                    VALUES (%s, %s, %s, %s, %s)''',
                    (dia_id, exercicio['exercicio_id'], exercicio['series'], 
                     exercicio['repeticoes'], exercicio['descricao'])
                )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Plano de treino criado com sucesso', 'plano_id': plano_id})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/treinos/registrar', methods=['POST'])
def registrar_treino():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))
    
    user_id = session['usuario_id']
    data = request.get_json()
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''INSERT INTO historico_treinos 
            (usuario_id, data, tipo_treino, duracao, calorias, observacoes)
            VALUES (%s, %s, %s, %s, %s, %s)''',
            (user_id, data['data'], data['tipo_treino'], data['duracao'], 
             data['calorias'], data['observacoes'])
        )
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Treino registrado com sucesso'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# New routes for the updated interface
@app.route('/equipamentos')
def equipamentos():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))
    
    return jsonify([
        {
            'nome': 'D1Fitness',
            'descricao': 'Loja especializada em equipamentos de academia para uso profissional e residencial.',
            'link': 'https://d1fitness.com.br',
            'imagem': 'logos/logod1.png'
        },
        {
            'nome': 'Natural Fitness',
            'descricao': 'Focada em acessórios e equipamentos de musculação como cordas, elásticos, halteres.',
            'link': 'https://naturalfitness.com.br/',
            'imagem': 'logos/logonatu.png'
        },
        {
            'nome': 'Kikos Fitness',
            'descricao': 'Marca tradicional (35+ anos) no setor fitness, com esteiras, bicicletas, elípticos.',
            'link': 'https://www.kikos.com.br/',
            'imagem': 'logos/logokikos.png'
        },
        {
            'nome': 'Casa do Fitness',
            'descricao': 'Loja especializada em musculação e cardio, com assistência técnica e suporte pós-venda.',
            'link': 'https://www.casadofitness.com.br/',
            'imagem': 'logos/logocasa.png'
        },
        {
            'nome': 'Rope Store',
            'descricao': 'Voltada para cross-training e funcional: anilhas olímpicas, barras, rigs, kettlebells.',
            'link': 'https://ropestore.com.br/',
            'imagem': 'logos/logorope.png'
        },
        {
            'nome': 'MegaGym',
            'descricao': 'Mais focada em halteres, kettlebells e kits de pesos acessíveis.',
            'link': 'https://megagym.com.br/',
            'imagem': 'logos/logomega.png'
        },
        {
            'nome': 'Rei do Fitness',
            'descricao': 'Fabrica e vende seus próprios equipamentos de musculação, funcional e cross-training.',
            'link': 'https://www.reidofitness.com.br/',
            'imagem': 'logos/logorei.png'
        },
        {
            'nome': 'Uplift Fitness',
            'descricao': 'Loja moderna com halteres, barras, racks e acessórios de alta qualidade.',
            'link': 'https://upliftfitness.com.br/',
            'imagem': 'logos/logoup.png'
        }
    ])

@app.route('/suplementos')
def suplementos():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))
    
    return jsonify([
        {
            'nome': 'Growth Supplements',
            'descricao': 'Loja online com grande variedade de suplementos e vitaminas.',
            'link': 'https://www.growth.com.br',
            'imagem': 'logos/logogrow.png'
        },
        {
            'nome': 'Madrugão Suplementos',
            'descricao': 'Oferece suplementos com foco em custo-benefício e entrega rápida.',
            'link': 'https://www.madrugaosuplementos.com.br',
            'imagem': 'logos/logonadru.png'
        },
        {
            'nome': 'Corpo Ideal',
            'descricao': 'Loja especializada em nutrição esportiva e produtos para ganho de massa e definição.',
            'link': 'https://www.corpoideal.com.br',
            'imagem': 'logos/logocorpo.png'
        },
        {
            'nome': 'Dux Nutrition',
            'descricao': 'Suplementos de alta qualidade, incluindo whey, creatina, BCAA e pré-treinos.',
            'link': 'https://www.duxnutrition.com.br',
            'imagem': 'logos/logodux.png'
        },
        {
            'nome': 'Max Titanium',
            'descricao': 'Marca brasileira renomada em suplementos, com linha completa de proteínas.',
            'link': 'https://www.maxtitanium.com.br',
            'imagem': 'logos/logomax.png'
        }
    ])

@app.route('/comunidade')
def comunidade():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))
    
    # Sample community data
    return jsonify({
        'grupos': [
            'Grupo de musculação',
            'Time de futebol',
            'Equipe de basquete',
            'Grupo de alongamento'
        ],
        'destaques': [
            'João aumentou 5kg no supino',
            'Maria correu 5km em 22min',
            'Carlos perdeu 3% de gordura'
        ]
    })

if __name__ == '__main__':
    app.run(debug=True)