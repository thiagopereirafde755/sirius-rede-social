from flask import Blueprint, render_template, request, session, redirect, url_for
from app.conexao import criar_conexao
from app.utils import render_swal_alert
from datetime import datetime, timedelta
from app.enviar_email import confirmacao_conta_email
import random
import string

login_bp = Blueprint('login', __name__)

# Duração da sessão de confirmação (15 minutos)
CONFIRMACAO_SESSION_LIFETIME = timedelta(minutes=15)

@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conexao = criar_conexao()

        if conexao:
            cursor = conexao.cursor(dictionary=True)  # Para pegar nomes das colunas
            cursor.execute("SELECT id, username, conta_confirmada FROM users WHERE email = %s AND senha = %s", (email, senha))
            usuario = cursor.fetchone()

            if usuario:
                usuario_id = usuario['id']
                conta_confirmada = usuario['conta_confirmada']
                username = usuario['username']

                if conta_confirmada == 1:
                    session.permanent = True
                    session['usuario_id'] = usuario_id
                    cursor.close()
                    conexao.close()
                    return redirect(url_for('inicio.inicio'))
                else:
                    # Gera código novo
                    codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                    codigo_gerado_em = datetime.now()

                    # Atualiza o código e o tempo no banco
                    cursor.execute("""
                        UPDATE users SET codigo_user = %s, codigo_user_gerado_em = %s
                        WHERE id = %s
                    """, (codigo, codigo_gerado_em, usuario_id))
                    conexao.commit()

                    # Envia o email com o código novo
                    confirmacao_conta_email(email, codigo, username)

                    # Cria a sessão para confirmação
                    session['email_confirmacao'] = email
                    session['confirmacao_expira'] = (datetime.now() + CONFIRMACAO_SESSION_LIFETIME).isoformat()
                    session['ultimo_envio'] = datetime.now().isoformat()

                    cursor.close()
                    conexao.close()

                    return render_swal_alert(f'''
                        <script>
                            Swal.fire({{
                                title: 'Confirmação Necessária',
                                text: 'Você precisa confirmar sua conta para poder usar la. Um código será enviado por e-mail.',
                                icon: 'warning',
                                confirmButtonText: 'Confirmar Conta',
                                confirmButtonColor: '#a76ab6',
                                background: '#2d2a32',
                                color: '#e0e0e0',
                                showCancelButton: true,
                                cancelButtonText: 'Cancelar',
                                cancelButtonColor: '#6c757d'
                            }}).then((result) => {{
                                if (result.isConfirmed) {{
                                    window.location.href = "{url_for('confirmar_conta.part1')}";
                                }} else {{
                                    window.location.href = "/";
                                }}
                            }});
                        </script>
                    ''')

            else:
                cursor.close()
                conexao.close()
                return render_template('index.html', email=email, erro='Email ou senha incorretos!')

        else:
            return render_swal_alert('''
                <script>
                    Swal.fire({
                        title: 'Erro de Conexão',
                        text: 'Não foi possível conectar ao banco de dados',
                        icon: 'error',
                        confirmButtonText: 'OK',
                        confirmButtonColor: '#a76ab6',
                        background: '#2d2a32',
                        color: '#e0e0e0'
                    }).then(() => {
                        window.location.href = "/";
                    });
                </script>
            ''')

    return render_template('index.html')
