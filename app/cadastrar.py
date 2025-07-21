from flask import Blueprint, render_template, request, redirect, session
from app.conexao import criar_conexao
from datetime import datetime, date, timedelta
import random
import string
from app.enviar_email import confirmacao_conta_email
from werkzeug.security import generate_password_hash

cadastrar_bp = Blueprint('cadastrar', __name__)

# SESSAO PARA CONFIRMAR CONTA
CONFIRMACAO_SESSION_LIFETIME = timedelta(minutes=15)

# =============================================================
#  CADASTRAR USUARIO
# =============================================================
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

            # VERIFICA SE O USERNAME EXISTE
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                erros['username'] = "Este nome de usuário já está em uso"
            
            # VERIFICA SE O EMAIL EXISTE
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                erros['email'] = "Este e-mail já está cadastrado"
            
            # VERIFICA A IDADE MINIMA
            nascimento = datetime.strptime(data_nascimento, '%Y-%m-%d').date()
            hoje = date.today()
            idade = hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))
            if idade < 13:
                erros['idade'] = "Você deve ter pelo menos 13 anos para se cadastrar"

            # VERIFICA SE AS SENHAS SAO IGUAIS
            if senha != confirmar_senha:
                erros['senha'] = "As senhas não coincidem"
            
            if erros:
                cursor.close()
                conexao.close()
                return render_template('cadastro.html', erros=erros, form_data=request.form)
            
            # GERA O CODIGO DE CONFIRMAÇAO
            codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            codigo_gerado_em = datetime.now()

            # INSERA O USER NO BANCO MAIS NAO CONFIRMA A CONTA
            cursor.execute("""
                INSERT INTO users 
                (nome, username, email, senha, data_nascimento, codigo_user, codigo_user_gerado_em, conta_confirmada) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (nome, username, email, generate_password_hash(senha), data_nascimento, codigo, codigo_gerado_em, 0))
            
            conexao.commit()
            cursor.close()
            conexao.close()

            # SESSAO TEMPORARIA PARA CONFIRMAR CONTA
            session['email_confirmacao'] = email
            session['confirmacao_expira'] = (datetime.now() + CONFIRMACAO_SESSION_LIFETIME).isoformat()
            session['ultimo_envio'] = datetime.now().isoformat()

            # ENVIA O EMAIL DE CONFIRMAÇÃO
            confirmacao_conta_email(email, codigo, username)

            # LEVA A PAGINA PARA CONFIRMA CONTA
            return redirect('/confirmar_conta/part1')
        else:
            return '<script>alert("Erro ao conectar ao banco de dados!"); window.location.href = "/cadastro";</script>'

    return redirect('/')