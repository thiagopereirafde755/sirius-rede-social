from flask import Blueprint, render_template, request, session, redirect, url_for, flash, jsonify
import random
from app.conexao import criar_conexao
from datetime import datetime, timedelta
from app.enviar_email import recuperacao_senha_user_logado
import random
from app.utils import buscar_hashtags_mais_usadas
from werkzeug.security import generate_password_hash

recuperar_senha_logado_bp = Blueprint('recuperar_senha_logado', __name__)

# =============================================================
#  REENVIA O CODIGO
# =============================================================
@recuperar_senha_logado_bp.route('/reenviar_codigo', methods=['POST'])
def reenviar_codigo():
    if 'usuario_id' not in session:
        return 'Não autorizado', 401

    usuario_id = session['usuario_id']
    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    try:
        # BUSCA AS INFORMAÇAO DO USER
        cursor.execute("SELECT email, username FROM users WHERE id = %s", (usuario_id,))
        user = cursor.fetchone()

        if not user:
            return 'Usuário não encontrado', 404

        email_usuario = user['email']
        nome_usuario = user['username']
        agora = datetime.now()

        # INVALIDA OS CODIGOS ANTERIORES
        cursor.execute("""
            UPDATE recuperacao_senha 
            SET expirado_em = %s 
            WHERE user_id = %s 
              AND utilizado_em IS NULL 
              AND expirado_em IS NULL
        """, (agora, usuario_id))

        # GERA UM NOVO CODIGO
        codigo = str(random.randint(100000, 999999))

        # SALVA NO BD
        cursor.execute("""
            INSERT INTO recuperacao_senha (user_id, codigo, criado_em, ip_criacao)
            VALUES (%s, %s, %s, %s)
        """, (usuario_id, codigo, agora, request.remote_addr))
        conexao.commit()

        # ENVIA O EMAIL E O CODIGO
        recuperacao_senha_user_logado(email_usuario, codigo, nome_usuario)

        return 'Código reenviado com sucesso', 200

    except Exception as e:
        print("Erro ao reenviar código:", e)
        return 'Erro interno ao reenviar código', 500

    finally:
        cursor.close()
        conexao.close()
# =============================================================
#  PARTE 1 PARA RECUPERAR SENHA
# =============================================================
@recuperar_senha_logado_bp.route('/recuperar_senha_logado_part1', methods=['GET', 'POST'])
def recuperar_senha_logado_part1():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']
    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    try:

        # HASHTAG DO MOMENTO
        hashtags_top = buscar_hashtags_mais_usadas(cursor)

        # INFORMAÇAO DO USER
        cursor.execute("""
            SELECT nome, username, fotos_perfil, bio, foto_capa, perfil_publico,
                   comentarios_publicos, visibilidade_seguidores, tema, curtidas_publicas,
                   audio_notificacoes, audio_notificacoes_mensagem, email, online, ultima_atividade, modo_status
            FROM users
            WHERE id = %s
        """, (usuario_id,))
        usuario = cursor.fetchone()

        # REDERIZAR PARA O HTML
        nome_completo = usuario.get('nome') if usuario else None
        nome_usuario = usuario.get('username') if usuario else None
        foto_perfil = usuario['fotos_perfil'] if usuario and usuario['fotos_perfil'] else url_for('static', filename='img/icone/user.png')
        bio_user = usuario.get('bio') if usuario else None
        foto_capa = usuario['foto_capa'] if usuario and usuario['foto_capa'] else url_for('static', filename='img/icone/redes-sociais-capa-1.jpg')
        perfil_publico = usuario['perfil_publico'] if usuario and usuario['perfil_publico'] is not None else True
        comentarios_publicos = usuario['comentarios_publicos'] if usuario and usuario['comentarios_publicos'] is not None else True
        visibilidade_seguidores = usuario['visibilidade_seguidores'] if usuario and usuario['visibilidade_seguidores'] else 'publico'
        tema = usuario.get('tema', 'claro') if usuario else 'claro'
        curtidas_publicas = usuario.get('curtidas_publicas', True) if usuario else True
        audio_notificacoes = usuario.get('audio_notificacoes', True) if usuario else True
        audio_notificacoes_mensagem = usuario.get('audio_notificacoes_mensagem', True) if usuario else True
        online = usuario.get('online', 0) if usuario else 0
        ultima_atividade = usuario.get('ultima_atividade') if usuario else None
        modo_status = usuario.get('modo_status', 'normal') if usuario else 'normal'
        email_usuario = usuario.get('email') if usuario else None

        if request.method == 'POST':
            email_digitado = request.form.get('email')
            if email_digitado != email_usuario:
                return render_template('recuperar_senha_logado_part1.html',
                    nome=nome_completo, username=nome_usuario, foto_perfil=foto_perfil, bio=bio_user,
                    foto_capa=foto_capa, perfil_publico=perfil_publico, comentarios_publicos=comentarios_publicos,
                    visibilidade_seguidores=visibilidade_seguidores, tema=tema, curtidas_publicas=curtidas_publicas,
                    audio_notificacoes=audio_notificacoes, audio_notificacoes_mensagem=audio_notificacoes_mensagem,
                    online=online, ultima_atividade=ultima_atividade, modo_status=modo_status,
                    hashtags_top=hashtags_top, erro_email=True
                )
            
            session.pop('codigo_validado', None)
            
            # INVALIDA TODOS OS CODIGOS ANTERIORES
            agora = datetime.now()
            cursor.execute("""
                UPDATE recuperacao_senha 
                SET expirado_em = %s 
                WHERE user_id = %s 
                AND utilizado_em IS NULL 
                AND expirado_em IS NULL
            """, (agora, usuario_id))

            # GERA UM NOVO CODIGO E SALVA NO BANCO
            codigo = str(random.randint(100000, 999999))
            cursor.execute("""
                INSERT INTO recuperacao_senha (user_id, codigo, criado_em, ip_criacao)
                VALUES (%s, %s, %s, %s)
            """, (usuario_id, codigo, agora, request.remote_addr))
            conexao.commit()

            recuperacao_senha_user_logado(email_digitado, codigo, nome_usuario)
            return redirect(url_for('.recuperar_senha_logado_part2'))

        return render_template('recuperar_senha_logado_part1.html',
            nome=nome_completo, username=nome_usuario, foto_perfil=foto_perfil, bio=bio_user,
            foto_capa=foto_capa, perfil_publico=perfil_publico, comentarios_publicos=comentarios_publicos,
            visibilidade_seguidores=visibilidade_seguidores, tema=tema, curtidas_publicas=curtidas_publicas,
            audio_notificacoes=audio_notificacoes, audio_notificacoes_mensagem=audio_notificacoes_mensagem,
            online=online, ultima_atividade=ultima_atividade, modo_status=modo_status,
            hashtags_top=hashtags_top
        )

    finally:
        cursor.close()
        conexao.close()
# =============================================================
#  PARTE 2 PARA RECUPERAR A SENHA
# ============================================================= 
@recuperar_senha_logado_bp.route('/recuperar_senha_logado_part2', methods=['GET', 'POST'])
def recuperar_senha_logado_part2():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']
    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    try:
        # HASHTAG DO MOMENTO
        hashtags_top = buscar_hashtags_mais_usadas(cursor)

        # INFORMAÇAO DO USER
        cursor.execute("""
            SELECT nome, username, fotos_perfil, bio, foto_capa, perfil_publico,
                   comentarios_publicos, visibilidade_seguidores, tema, curtidas_publicas,
                   audio_notificacoes, audio_notificacoes_mensagem, online, ultima_atividade, modo_status
            FROM users WHERE id = %s
        """, (usuario_id,))
        usuario = cursor.fetchone()

        # PARA O HTML
        template_params = {
            'nome': usuario.get('nome'),
            'username': usuario.get('username'),
            'foto_perfil': usuario['fotos_perfil'] if usuario and usuario['fotos_perfil'] else url_for('static', filename='img/icone/user.png'),
            'bio': usuario.get('bio'),
            'foto_capa': usuario['foto_capa'] if usuario and usuario['foto_capa'] else url_for('static', filename='img/icone/redes-sociais-capa-1.jpg'),
            'perfil_publico': usuario['perfil_publico'] if usuario and usuario['perfil_publico'] is not None else True,
            'comentarios_publicos': usuario['comentarios_publicos'] if usuario and usuario['comentarios_publicos'] is not None else True,
            'visibilidade_seguidores': usuario['visibilidade_seguidores'] if usuario and usuario['visibilidade_seguidores'] else 'publico',
            'tema': usuario.get('tema', 'claro'),
            'curtidas_publicas': usuario.get('curtidas_publicas', True),
            'audio_notificacoes': usuario.get('audio_notificacoes', True),
            'audio_notificacoes_mensagem': usuario.get('audio_notificacoes_mensagem', True),
            'online': usuario.get('online', 0),
            'ultima_atividade': usuario.get('ultima_atividade'),
            'modo_status': usuario.get('modo_status', 'normal'),
            'hashtags_top': hashtags_top
        }

        if request.method == 'POST':
            codigo_digitado = request.form.get('codigo')
            agora = datetime.now()

            # BUSCAR CODIGO VALIDO
            cursor.execute("""
                SELECT id, criado_em FROM recuperacao_senha
                WHERE user_id=%s AND codigo=%s AND utilizado_em IS NULL AND expirado_em IS NULL
                AND criado_em >= %s
                ORDER BY criado_em DESC LIMIT 1
            """, (usuario_id, codigo_digitado, agora - timedelta(minutes=15)))
            row = cursor.fetchone()

            if row:
                # MARCA COMO UTILIZADO
                cursor.execute("UPDATE recuperacao_senha SET utilizado_em=%s WHERE id=%s", (agora, row['id']))
                conexao.commit()
                session['codigo_validado'] = True
                return redirect(url_for('.recuperar_senha_logado_part3'))
            else:
                # EXPIRA O CODIGO NAO USADO
                cursor.execute("""
                    UPDATE recuperacao_senha SET expirado_em=%s
                    WHERE user_id=%s AND utilizado_em IS NULL AND expirado_em IS NULL AND criado_em < %s
                """, (agora, usuario_id, agora - timedelta(minutes=15)))
                conexao.commit()
                
                # ADCIONA MSG DE ERRO
                template_params.update({
                    'erro_codigo': True,
                    'mensagem_erro': 'Código inválido ou expirado. Por favor, tente novamente.'
                })

        return render_template('recuperar_senha_logado_part2.html', **template_params)

    finally:
        cursor.close()
        conexao.close()
# =============================================================
#  PARTE 3 PARA RECUPERAR A SENHA
# ============================================================= 
@recuperar_senha_logado_bp.route('/recuperar_senha_logado_part3', methods=['GET', 'POST'])
def recuperar_senha_logado_part3():
    if 'usuario_id' not in session:
        if request.method == 'POST':
            return jsonify({'success': False, 'error': 'Sessão expirada. Faça login novamente.'}), 401
        return redirect(url_for('index'))
    
    if not session.get('codigo_validado'):
        return redirect(url_for('.recuperar_senha_logado_part2'))

    usuario_id = session['usuario_id']
    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    try:
        # VERIFICA SE O CODIGO E VALIDO
        cursor.execute("""
            SELECT 1 FROM recuperacao_senha
            WHERE user_id=%s AND utilizado_em IS NOT NULL AND expirado_em IS NULL
            AND utilizado_em >= NOW() - INTERVAL 5 MINUTE
            ORDER BY utilizado_em DESC LIMIT 1
        """, (usuario_id,))
        codigo_valido = cursor.fetchone()
        
        if not codigo_valido and not session.get('codigo_validado'):
            return redirect(url_for('.recuperar_senha_logado_part2'))

        # HASHTAG DO MOMENTO
        hashtags_top = buscar_hashtags_mais_usadas(cursor)

        # BUSCA A INFORMAÇÃO DO USER
        cursor.execute("""
            SELECT nome, username, fotos_perfil, bio, foto_capa, perfil_publico,
                   comentarios_publicos, visibilidade_seguidores, tema, curtidas_publicas,
                   audio_notificacoes, audio_notificacoes_mensagem, online, ultima_atividade, modo_status
            FROM users WHERE id = %s
        """, (usuario_id,))
        usuario = cursor.fetchone()

        # PARA O HTML
        template_params = {
            'nome': usuario.get('nome'),
            'username': usuario.get('username'),
            'foto_perfil': usuario['fotos_perfil'] if usuario and usuario['fotos_perfil'] else url_for('static', filename='img/icone/user.png'),
            'bio': usuario.get('bio'),
            'foto_capa': usuario['foto_capa'] if usuario and usuario['foto_capa'] else url_for('static', filename='img/icone/redes-sociais-capa-1.jpg'),
            'perfil_publico': usuario['perfil_publico'] if usuario and usuario['perfil_publico'] is not None else True,
            'comentarios_publicos': usuario['comentarios_publicos'] if usuario and usuario['comentarios_publicos'] is not None else True,
            'visibilidade_seguidores': usuario['visibilidade_seguidores'] if usuario and usuario['visibilidade_seguidores'] else 'publico',
            'tema': usuario.get('tema', 'claro'),
            'curtidas_publicas': usuario.get('curtidas_publicas', True),
            'audio_notificacoes': usuario.get('audio_notificacoes', True),
            'audio_notificacoes_mensagem': usuario.get('audio_notificacoes_mensagem', True),
            'online': usuario.get('online', 0),
            'ultima_atividade': usuario.get('ultima_atividade'),
            'modo_status': usuario.get('modo_status', 'normal'),
            'hashtags_top': hashtags_top
        }

        if request.method == 'GET':
            return render_template('recuperar_senha_logado_part3.html', **template_params)

        data = request.get_json() if request.is_json else request.form
        nova_senha = data.get('nova_senha')
        confirmar_senha = data.get('confirmar_senha')

        # VALIDAÇAO DO CAMPO DE SENHA
        if not nova_senha or not confirmar_senha:
            return jsonify({'success': False, 'error': 'Informe e confirme a nova senha.'}), 400

        if len(nova_senha) < 6:
            return jsonify({'success': False, 'error': 'A senha deve ter pelo menos 6 caracteres.'}), 400

        if nova_senha != confirmar_senha:
            return jsonify({'success': False, 'error': 'As senhas não coincidem.'}), 400

        # ATUALIZA A SENHA E INVALIDA O CODIGO USADO
        senha_hash = generate_password_hash(nova_senha)
        cursor.execute("UPDATE users SET senha = %s WHERE id = %s", (senha_hash, usuario_id))
        
        cursor.execute("""
            UPDATE recuperacao_senha 
            SET expirado_em = %s 
            WHERE user_id = %s 
            AND utilizado_em IS NULL 
            AND expirado_em IS NULL
        """, (datetime.now(), usuario_id))
        
        conexao.commit()
        session.pop('codigo_validado', None)
        
        return jsonify({
            'success': True,
            'message': 'Senha alterada com sucesso!',
            'redirect': url_for('configuracao.configuracao')
        }), 200

    except Exception as e:
        conexao.rollback()
        if request.method == 'POST':
            return jsonify({'success': False, 'error': 'Erro interno no servidor.'}), 500
        flash('Ocorreu um erro ao processar sua solicitação.', 'error')
        return redirect(url_for('configuracao.configuracao'))
    finally:
        cursor.close()
        conexao.close()