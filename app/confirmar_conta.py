from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from app.conexao import criar_conexao
from app.enviar_email import confirmacao_conta_email 
import random
import string

confirmar_bp = Blueprint('confirmar_conta', __name__)

# Duração da sessão de confirmação (15 minutos)
CONFIRMACAO_SESSION_LIFETIME = timedelta(minutes=15)

def gerar_codigo():
    return ''.join(random.choices(string.digits, k=6))

@confirmar_bp.route('/confirmar_conta/part1', methods=['GET', 'POST'])
def part1():
    # Sessão de validação
    if 'email_confirmacao' not in session or \
       datetime.now() > datetime.fromisoformat(session.get('confirmacao_expira', '1970-01-01')):
        session.pop('email_confirmacao', None)
        session.pop('confirmacao_expira', None)
        return redirect('/')

    email = session['email_confirmacao']

    if request.method == 'POST':
        data = request.get_json()
        if not data or 'codigo' not in data:
            return jsonify({'success': False, 'message': 'Código não informado.'})
        
        codigo = data.get('codigo', '').strip()
        if not codigo:
            return jsonify({'success': False, 'message': 'Código não informado.'})

        conexao = criar_conexao()
        if conexao:
            try:
                cursor = conexao.cursor(dictionary=True)
                cursor.execute("SELECT id, codigo_user, codigo_user_gerado_em FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()

                if not user or not user['codigo_user']:
                    return jsonify({'success': False, 'message': 'Código não gerado para esta conta.'})

                tempo_expiracao = datetime.now() - timedelta(minutes=15)

                if user['codigo_user'] == codigo and user['codigo_user_gerado_em'] > tempo_expiracao:
                    # Confirma a conta
                    cursor.execute("UPDATE users SET conta_confirmada = 1 WHERE email = %s", (email,))
                    conexao.commit()

                    # Inicia sessão como no login
                    session.permanent = True
                    session['usuario_id'] = user['id']

                    # Limpa dados da sessão de confirmação
                    session.pop('email_confirmacao', None)
                    session.pop('confirmacao_expira', None)

                    return jsonify({'success': True, 'redirect': url_for('inicio.inicio')})
                else:
                    return jsonify({'success': False, 'message': 'Código inválido ou expirado.'})

            except Exception as e:
                print(f"Erro ao confirmar conta: {str(e)}")
                return jsonify({'success': False, 'message': 'Erro interno ao processar.'})
            finally:
                cursor.close()
                conexao.close()

    return render_template('confirmar_conta_part1.html')



@confirmar_bp.before_request
def verificar_sessao_confirmacao():
    # Verifica apenas nas rotas de confirmação
    if request.endpoint and request.endpoint.startswith('confirmar_conta.'):
        # Se estiver na part1 e a sessão tiver expirado
        if request.endpoint == 'confirmar_conta.part1' and \
           'email_confirmacao' in session and \
           datetime.now() > datetime.fromisoformat(session.get('confirmacao_expira', '1970-01-01')):
            
            session.pop('email_confirmacao', None)
            session.pop('confirmacao_expira', None)
            return redirect('/')
    
@confirmar_bp.route('/limpar_sessao_confirmacao', methods=['POST'])
def limpar_sessao_confirmacao():
    session.pop('email_confirmacao', None)
    session.pop('confirmacao_expira', None)
    return '', 204

@confirmar_bp.route('/refresh_sessao_confirmacao', methods=['POST'])
def refresh_sessao_confirmacao():
    if 'email_confirmacao' in session:
        session['confirmacao_expira'] = (datetime.now() + CONFIRMACAO_SESSION_LIFETIME).isoformat()
    return '', 204

@confirmar_bp.route('/reenviar_codigo', methods=['POST'])
def reenviar_codigo():
    if 'email_confirmacao' not in session:
        return jsonify({'success': False, 'message': 'Sessão expirada'})
    
    email = session['email_confirmacao']
    codigo = gerar_codigo()
    agora = datetime.now()
    
    # Primeiro atualiza no banco de dados
    conexao = criar_conexao()
    if conexao:
        try:
            cursor = conexao.cursor()
            cursor.execute(
                "UPDATE users SET codigo_user = %s, codigo_user_gerado_em = %s WHERE email = %s",
                (codigo, agora, email)
            )
            conexao.commit()
            
            # Obtém o username para o e-mail
            cursor.execute("SELECT username FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            username = user[0] if user else "Usuário"
            
            # Responde rápido e deixa o e-mail ser enviado em background
            from threading import Thread
            Thread(target=confirmacao_conta_email, args=(email, codigo, username)).start()
            
            # Atualiza o tempo de expiração da sessão
            session['confirmacao_expira'] = (agora + CONFIRMACAO_SESSION_LIFETIME).isoformat()
            return jsonify({'success': True})
            
        except Exception as e:
            print(f"Erro ao reenviar código: {e}")
            return jsonify({'success': False, 'message': 'Erro interno'})
        
        finally:
            cursor.close()
            conexao.close()
    
    return jsonify({'success': False, 'message': 'Erro de conexão'})