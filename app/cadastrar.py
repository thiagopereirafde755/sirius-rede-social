from flask import Blueprint, render_template, request, redirect, session
from app.conexao import criar_conexao
from datetime import datetime, date, timedelta
import random
import string
from app.enviar_email import confirmacao_conta_email

cadastrar_bp = Blueprint('cadastrar', __name__)

# Duração da sessão de confirmação (15 minutos)
CONFIRMACAO_SESSION_LIFETIME = timedelta(minutes=15)

@cadastrar_bp.route('/cadastrar', methods=['GET', 'POST'])
def cadastrar():
    if request.method == 'POST':
        nome = request.form['nome']
        username = request.form['username']
        email = request.form['email']
        senha = request.form['senha']
        confirmar_senha = request.form.get('confirmar_senha', '')
        data_nascimento = request.form['data_nascimento']
        
        erros = {}
        
        conexao = criar_conexao()
        if conexao:
            cursor = conexao.cursor()

            # Verifica se username já existe
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                erros['username'] = "Este nome de usuário já está em uso"
            
            # Verifica se e-mail já existe
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                erros['email'] = "Este e-mail já está cadastrado"
            
            # Verifica idade mínima
            nascimento = datetime.strptime(data_nascimento, '%Y-%m-%d').date()
            hoje = date.today()
            idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
            if idade < 13:
                erros['idade'] = "Você deve ter pelo menos 13 anos para se cadastrar"

            # Verifica se senhas coincidem
            if senha != confirmar_senha:
                erros['senha'] = "As senhas não coincidem"
            
            if erros:
                cursor.close()
                conexao.close()
                return render_template('cadastro.html', erros=erros, form_data=request.form)
            
            # Gera código de confirmação
            codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            codigo_gerado_em = datetime.now()

            # Insere usuário no banco com conta_confirmada = 0
            cursor.execute("""
                INSERT INTO users 
                (nome, username, email, senha, data_nascimento, codigo_user, codigo_user_gerado_em, conta_confirmada) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (nome, username, email, senha, data_nascimento, codigo, codigo_gerado_em, 0))
            
            conexao.commit()
            cursor.close()
            conexao.close()

            # Configura sessão temporária de confirmação
            session['email_confirmacao'] = email
            session['confirmacao_expira'] = (datetime.now() + CONFIRMACAO_SESSION_LIFETIME).isoformat()
            session['ultimo_envio'] = datetime.now().isoformat()

            # Envia e-mail de confirmação
            confirmacao_conta_email(email, codigo, username)

            # Redireciona diretamente para a página de confirmação (part1)
            return redirect('/confirmar_conta/part1')
        else:
            return '<script>alert("Erro ao conectar ao banco de dados!"); window.location.href = "/cadastro";</script>'

    return redirect('/')