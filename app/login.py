from flask import Blueprint, render_template, request, session, redirect, url_for
from app.conexao import criar_conexao
from app.utils import render_swal_alert
from datetime import datetime, timedelta
from app.enviar_email import confirmacao_conta_email, enviar_email_login
import random
import string
import threading
import requests
from user_agents import parse
import uuid
from werkzeug.security import check_password_hash

login_bp = Blueprint('login', __name__)

# DURAÇAO DA SESSAO PARA A PAGINA DE CONFIRMAR CONTA 15 MIN
CONFIRMACAO_SESSION_LIFETIME = timedelta(minutes=15)

# =============================================================
#  EMAIL EM SEGUNDO PLANO EM LOGIN
# =============================================================
def enviar_email_login_background(email, username, regiao, data_hora, dispositivo):
    try:
        enviar_email_login(email, username, regiao, data_hora, dispositivo)
    except Exception as e:
        print(f"[Erro ao enviar e-mail de login] {e}")
# =============================================================
#  PARA PEGAR A LOCALIZAÇAO DE QUEM LOGOU
# =============================================================
def get_location(ip):
    try:
        res = requests.get(f'http://ip-api.com/json/{ip}?lang=pt')
        data = res.json()
        if data['status'] == 'success':
            return f"{data.get('country', '')}, {data.get('regionName', '')}, {data.get('city', '')}"
        else:
            return "Localização desconhecida"
    except Exception:
        return "Localização desconhecida"
# =============================================================
#  PARA PEGAR A LOCALIZAÇAO DE QUEM LOGOU
# =============================================================
def get_location(ip):
    try:
        res = requests.get(f'http://ip-api.com/json/{ip}?lang=pt')
        data = res.json()
        if data['status'] == 'success':
            return f"{data.get('country', '')}, {data.get('regionName', '')}, {data.get('city', '')}"
        else:
            return "Localização desconhecida"
    except Exception:
        return "Localização desconhecida"
# =============================================================
#  PARA FAZER LOGIN
# =============================================================
@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']

        conexao = criar_conexao()
        if not conexao:
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

        cursor = conexao.cursor(dictionary=True)
        cursor.execute("SELECT id, username, senha, conta_confirmada, suspenso FROM users WHERE email = %s", (email,))
        usuario = cursor.fetchone()

        if usuario and check_password_hash(usuario['senha'], senha):
            if usuario['suspenso'] == 1:
                cursor.close()
                conexao.close()
                return render_swal_alert('''
                    <script>
                        Swal.fire({
                            title: 'Conta Suspensa',
                            text: 'Sua conta está suspensa. Contate o suporte para mais informações.',
                            icon: 'error',
                            confirmButtonText: 'OK',
                            confirmButtonColor: '#a76ab6',
                            background: '#2d2a32',
                            color: '#e0e0e0'
                        }).then(() => {
                            window.location.href = "/login";
                        });
                    </script>
                ''')

            if usuario['conta_confirmada'] == 1:
                
                # SESSAO DO DISPOSITIVO
                token = str(uuid.uuid4())
                cursor.execute("UPDATE users SET token_sessao = %s WHERE id = %s", (token, usuario['id']))
                conexao.commit()

                # SE A CONTA ESTA CONFIRMADA ENTRA E ENVIA O EMAIL
                ip = request.headers.get('X-Forwarded-For', request.remote_addr)
                regiao = get_location(ip)
                data_hora = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

                ua_string = request.headers.get('User-Agent', '')
                user_agent = parse(ua_string)
                dispositivo = "Desconhecido"
                if user_agent.is_mobile:
                    dispositivo = "Mobile"
                elif user_agent.is_tablet:
                    dispositivo = "Tablet"
                elif user_agent.is_pc:
                    dispositivo = "PC"
                elif user_agent.is_bot:
                    dispositivo = "Bot"

                navegador = user_agent.browser.family
                so = user_agent.os.family
                dispositivo_str = f"{dispositivo} - {so} - {navegador}"

                threading.Thread(
                    target=enviar_email_login_background,
                    args=(email, usuario['username'], regiao, data_hora, dispositivo_str)
                ).start()

                session.permanent = True
                session['usuario_id'] = usuario['id']
                session['token_sessao'] = token
                cursor.close()
                conexao.close()
                return redirect(url_for('inicio.inicio'))

            else:

                # SE A CONTA NAO FOI CONFIRMA GERA O CODIGO E ENVIA O EMAIL
                codigo = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
                codigo_gerado_em = datetime.now()

                cursor.execute("""
                    UPDATE users SET codigo_user = %s, codigo_user_gerado_em = %s
                    WHERE id = %s
                """, (codigo, codigo_gerado_em, usuario['id']))
                conexao.commit()

                # CAPTURA O DISPOSITIVO DO LOGIN
                ua_string = request.headers.get('User-Agent', '')
                user_agent = parse(ua_string)
                dispositivo = "Desconhecido"
                if user_agent.is_mobile:
                    dispositivo = "Mobile"
                elif user_agent.is_tablet:
                    dispositivo = "Tablet"
                elif user_agent.is_pc:
                    dispositivo = "PC"
                elif user_agent.is_bot:
                    dispositivo = "Bot"

                navegador = user_agent.browser.family
                so = user_agent.os.family
                info_login = f"Dispositivo: {dispositivo}, SO: {so}, Navegador: {navegador}"

                # ENVIA O CODIGO PARA CONFIRMAR CONTA
                confirmacao_conta_email(email, codigo, usuario['username'])

                session['email_confirmacao'] = email
                session['confirmacao_expira'] = (datetime.now() + CONFIRMACAO_SESSION_LIFETIME).isoformat()
                session['ultimo_envio'] = datetime.now().isoformat()

                cursor.close()
                conexao.close()

                return render_swal_alert(f'''
                    <script>
                        Swal.fire({{
                            title: 'Confirmação Necessária',
                            html: `Você precisa confirmar sua conta para poder usar-la. Um código foi enviado para {email}. <br><br>
                                    <br><br>
                                   `,
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

    return render_template('index.html')
# =============================================================
#  PARA NAO DEIXAR DOIS DISPOSTIVOS CONECTADO AO MESMO TEMPO
# =============================================================
@login_bp.route('/check_session')
def check_session():
    if 'usuario_id' not in session or 'token_sessao' not in session:
        return {'valid': False}

    usuario_id = session['usuario_id']
    token_sessao = session['token_sessao']

    conexao = criar_conexao()
    if not conexao:
        return {'valid': False}

    with conexao.cursor() as cursor:
        cursor.execute("SELECT token_sessao FROM users WHERE id = %s", (usuario_id,))
        row = cursor.fetchone()
    
    conexao.close()

    if not row:
        return {'valid': False}

    return {'valid': row[0] == token_sessao}