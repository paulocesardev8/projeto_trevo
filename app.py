from flask import Flask, render_template, request, redirect, session
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'segredo_trevo_2025'

# Função para criar as tabelas
def criar_tabelas():
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()

    # Tabela de famílias
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS familias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT,
            cpf TEXT,
            telefone TEXT,
            endereco TEXT,
            data_nascimento TEXT
        )
    ''')

    # Tabela de trabalhadores (usuários do sistema)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trabalhadores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            senha TEXT
        )
    ''')

    # Tabelas complementares
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS info_complementar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            familia_id INTEGER,
            genero TEXT,
            estado_civil TEXT,
            naturalidade TEXT,
            rg TEXT,
            bairro TEXT,
            cidade TEXT,
            escolaridade TEXT,
            profissao TEXT,
            FOREIGN KEY (familia_id) REFERENCES familias(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS composicao_familiar (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            familia_id INTEGER,
            nome TEXT,
            data_nascimento TEXT,
            parentesco TEXT,
            cpf TEXT,
            rg TEXT,
            trabalha_estuda TEXT,
            renda REAL,
            FOREIGN KEY (familia_id) REFERENCES familias(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS moradia (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            familia_id INTEGER,
            moradia TEXT,
            tipo_moradia TEXT,
            FOREIGN KEY (familia_id) REFERENCES familias(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS despesas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            familia_id INTEGER,
            habitacao REAL,
            agua REAL,
            energia REAL,
            telefone_internet REAL,
            gas REAL,
            medicamentos_insumos REAL,
            FOREIGN KEY (familia_id) REFERENCES familias(id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS outras_informacoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            familia_id INTEGER,
            auxilio_governo TEXT,
            valor_auxilio REAL,
            frequenta_cras TEXT,
            qual_auxilio TEXT,
            comorbidade TEXT,
            observacoes TEXT,
            data_registro TEXT,
            FOREIGN KEY (familia_id) REFERENCES familias(id)
        )
    ''')

    conn.commit()
    conn.close()
    print("✔️ Tabelas criadas ou já existentes.")


@app.route('/')
def index():
    return redirect('/inicio')

@app.route('/login', methods=['GET', 'POST'])
def login():
    erro = None
    if request.method == 'POST':
        usuario = request.form['usuario']
        senha = request.form['senha']

        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM trabalhadores WHERE usuario = ? AND senha = ?", (usuario, senha))
        trabalhador = cursor.fetchone()
        conn.close()

        if trabalhador:
            session['usuario'] = usuario
            session['mensagem'] = 'Login realizado com sucesso!'
            return redirect('/inicio')
        else:
            erro = 'Usuário ou senha inválidos.'
    return render_template('login.html', erro=erro)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect('/login')

@app.route('/inicio')
def inicio():
    if 'usuario' not in session:
        return redirect('/login')
    return render_template('inicio.html')

@app.route('/cadastro', methods=['GET', 'POST'])
def cadastro():
    if 'usuario' not in session:
        return redirect('/login')
    if request.method == 'POST':
        nome = request.form['nome']
        cpf = request.form['cpf']
        telefone = request.form['telefone']
        endereco = request.form['endereco']
        data_nascimento = request.form.get('data_nascimento') or None

        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO familias (nome, cpf, telefone, endereco, data_nascimento)
            VALUES (?, ?, ?, ?, ?)
        ''', (nome, cpf, telefone, endereco, data_nascimento))
        conn.commit()
        

        # Pegar o ID da família recém cadastrada
        familia_id = cursor.lastrowid
        conn.close()
        
        return redirect(f'/cadastro_info/{familia_id}')
    
    return render_template('cadastro.html')


# --- Cadastro de Informações Complementares ---
@app.route('/cadastro_info/<int:familia_id>', methods=['GET', 'POST'])
def cadastro_info(familia_id):
    if 'usuario' not in session:
        return redirect('/login')
    
    if request.method == 'POST':
        genero = request.form['genero']
        estado_civil = request.form['estado_civil']
        naturalidade = request.form['naturalidade']
        rg = request.form['rg']
        bairro = request.form['bairro']
        cidade = request.form['cidade']
        escolaridade = request.form['escolaridade']
        profissao = request.form['profissao']

        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO info_complementar
            (familia_id, genero, estado_civil, naturalidade, rg, bairro, cidade, escolaridade, profissao)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (familia_id, genero, estado_civil, naturalidade, rg, bairro, cidade, escolaridade, profissao))
        conn.commit()
        conn.close()

        # Redirecionar para a próxima etapa (composição familiar)
        return redirect(f'/cadastro_membros/{familia_id}')
    
    return render_template('cadastro_info.html', familia_id=familia_id)

# --- Cadastro de Composição Familiar ---
@app.route('/cadastro_membros/<int:familia_id>', methods=['GET', 'POST'])
def cadastro_membros(familia_id):
    if 'usuario' not in session:
        return redirect('/login')

    if request.method == 'POST':
        nome = request.form['nome']
        data_nascimento = request.form['data_nascimento']
        parentesco = request.form['parentesco']
        cpf = request.form['cpf']
        rg = request.form['rg']
        trabalha_estuda = request.form['trabalha_estuda']
        renda = request.form['renda']

        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO composicao_familiar
            (familia_id, nome, data_nascimento, parentesco, cpf, rg, trabalha_estuda, renda)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (familia_id, nome, data_nascimento, parentesco, cpf, rg, trabalha_estuda, renda))
        conn.commit()
        conn.close()

        acao = request.form.get('acao')
        if acao == 'adicionar':
            return redirect(f'/cadastro_membros/{familia_id}')
        elif acao == 'avancar':
            return redirect(f'/cadastro_moradia/{familia_id}')  

    return render_template('cadastro_membros.html', familia_id=familia_id)

@app.route('/cadastro_moradia/<int:familia_id>', methods=['GET', 'POST'])
def cadastro_moradia(familia_id):
    if 'usuario' not in session:
        return redirect('/login')
    if request.method == 'POST':
        moradia = request.form['moradia']
        tipo_moradia = request.form['tipo_moradia']
        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO moradia (familia_id, moradia, tipo_moradia)
            VALUES (?, ?, ?)
        ''', (familia_id, moradia, tipo_moradia))
        conn.commit()
        conn.close()
        # Ir para próxima etapa: despesas
        return redirect(f'/cadastro_despesas/{familia_id}')
    return render_template('moradia.html', familia_id=familia_id)


@app.route('/cadastro_despesas/<int:familia_id>', methods=['GET', 'POST'])
def cadastro_despesas(familia_id):
    if 'usuario' not in session:
        return redirect('/login')
    if request.method == 'POST':
        habitacao = request.form['habitacao']
        agua = request.form['agua']
        energia = request.form['energia']
        telefone_internet = request.form['telefone_internet']
        gas = request.form['gas']
        medicamentos_insumos = request.form['medicamentos_insumos']
        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO despesas 
            (familia_id, habitacao, agua, energia, telefone_internet, gas, medicamentos_insumos)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (familia_id, habitacao, agua, energia, telefone_internet, gas, medicamentos_insumos))
        conn.commit()
        conn.close()
        # Ir para próxima etapa: outras informações
        return redirect(f'/cadastro_outras/{familia_id}')
    return render_template('despesas.html', familia_id=familia_id)


@app.route('/cadastro_outras/<int:familia_id>', methods=['GET', 'POST'])
def cadastro_outras(familia_id):
    if 'usuario' not in session:
        return redirect('/login')
    if request.method == 'POST':
        auxilio_governo = request.form['auxilio_governo']
        valor_auxilio = request.form['valor_auxilio']
        frequenta_cras = request.form['frequenta_cras']
        qual_auxilio = request.form['qual_auxilio']
        comorbidade = request.form['comorbidade']
        observacoes = request.form['observacoes']
        data_registro = datetime.now().strftime('%Y-%m-%d')
        conn = sqlite3.connect('banco.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO outras_informacoes
            (familia_id, auxilio_governo, valor_auxilio, frequenta_cras, qual_auxilio, comorbidade, observacoes, data_registro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (familia_id, auxilio_governo, valor_auxilio, frequenta_cras, qual_auxilio, comorbidade, observacoes, data_registro))
        conn.commit()
        conn.close()
        # Concluir o cadastro, voltando ao início
        return redirect('/inicio')
    return render_template('outras_informacoes.html', familia_id=familia_id)



@app.route('/familias')
def listar_familias():
    if 'usuario' not in session:
        return redirect('/login')

    cpf = request.args.get('cpf')
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    if cpf:
        cursor.execute('SELECT * FROM familias WHERE cpf = ?', (cpf,))
    else:
        cursor.execute('SELECT * FROM familias')
    familias = cursor.fetchall()
    conn.close()
    return render_template('familias.html', familias=familias, cpf=cpf)

@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar_familia(id):
    if 'usuario' not in session:
        return redirect('/login')
    
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    
    if request.method == 'POST':
        # Atualizar dados principais da família
        nome = request.form['nome']
        cpf = request.form['cpf']
        telefone = request.form['telefone']
        endereco = request.form['endereco']
        data_nascimento = request.form.get('data_nascimento', '')
        cursor.execute('''
            UPDATE familias
            SET nome = ?, cpf = ?, telefone = ?, endereco = ?, data_nascimento = ?
            WHERE id = ?
        ''', (nome, cpf, telefone, endereco, data_nascimento, id))

        # Atualizar informações complementares
        genero = request.form.get('genero', '')
        estado_civil = request.form.get('estado_civil', '')
        naturalidade = request.form.get('naturalidade', '')
        rg = request.form.get('rg', '')
        bairro = request.form.get('bairro', '')
        cidade = request.form.get('cidade', '')
        escolaridade = request.form.get('escolaridade', '')
        profissao = request.form.get('profissao', '')

        cursor.execute('SELECT id FROM info_complementar WHERE familia_id = ?', (id,))
        info_id = cursor.fetchone()
        if info_id:
            cursor.execute('''
                UPDATE info_complementar
                SET genero = ?, estado_civil = ?, naturalidade = ?, rg = ?, bairro = ?, cidade = ?, escolaridade = ?, profissao = ?
                WHERE familia_id = ?
            ''', (genero, estado_civil, naturalidade, rg, bairro, cidade, escolaridade, profissao, id))
        else:
            cursor.execute('''
                INSERT INTO info_complementar
                (familia_id, genero, estado_civil, naturalidade, rg, bairro, cidade, escolaridade, profissao)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (id, genero, estado_civil, naturalidade, rg, bairro, cidade, escolaridade, profissao))

        conn.commit()
        conn.close()
        return redirect('/familias')
    
    # GET: carregar dados para edição
    cursor.execute('SELECT * FROM familias WHERE id = ?', (id,))
    familia = cursor.fetchone()

    cursor.execute('SELECT * FROM info_complementar WHERE familia_id = ?', (id,))
    info_complementar = cursor.fetchone()

    conn.close()
    return render_template(
        'editar_familia.html',
        familia=familia,
        info_complementar=info_complementar
    )

@app.route('/deletar/<int:id>')
def deletar_familia(id):
    if 'usuario' not in session:
        return redirect('/login')
    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM familias WHERE id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect('/familias')

@app.template_filter('formatar_data')
def formatar_data(data_iso):
    try:
        data = datetime.strptime(data_iso, '%Y-%m-%d')
        return data.strftime('%d/%m/%Y')
    except:
        return data_iso or "Não informado"
    
@app.route('/visualizar/<int:id>')
def visualizar_familia(id):
    if 'usuario' not in session:
        return redirect('/login')

    conn = sqlite3.connect('banco.db')
    cursor = conn.cursor()

    # Dados principais da família
    cursor.execute('SELECT * FROM familias WHERE id = ?', (id,))
    familia = cursor.fetchone()

    # Informações complementares
    cursor.execute('SELECT * FROM info_complementar WHERE familia_id = ?', (id,))
    info_complementar = cursor.fetchone()

    # Composição familiar
    cursor.execute('SELECT * FROM composicao_familiar WHERE familia_id = ?', (id,))
    membros = cursor.fetchall()

    # Moradia
    cursor.execute('SELECT * FROM moradia WHERE familia_id = ?', (id,))
    moradia = cursor.fetchone()

    # Despesas
    cursor.execute('SELECT * FROM despesas WHERE familia_id = ?', (id,))
    despesas = cursor.fetchone()

    # Outras informações
    cursor.execute('SELECT * FROM outras_informacoes WHERE familia_id = ?', (id,))
    outras_infos = cursor.fetchone()

    conn.close()

    return render_template(
        'visualizar_familia.html',
        familia=familia,
        info_complementar=info_complementar,
        membros=membros,
        moradia=moradia,
        despesas=despesas,
        outras_infos=outras_infos
    )


if __name__ == '__main__':
    criar_tabelas()
    app.run(debug=True)
