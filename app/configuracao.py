from flask import Blueprint, render_template, redirect, url_for, session, request, flash, json, jsonify
from app.conexao import criar_conexao
from app.utils import buscar_hashtags_mais_usadas
from werkzeug.security import check_password_hash, generate_password_hash

configuracao_bp = Blueprint('configuracao', __name__)

# =============================================================
#  PAGINA DE CONFIGURACAO
# =============================================================
@configuracao_bp.route('/configuracao')
def configuracao():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT nome, username, fotos_perfil, bio, foto_capa, perfil_publico, comentarios_publicos, visibilidade_seguidores, tema,
                           curtidas_publicas, audio_notificacoes, audio_notificacoes_mensagem, codigo_user, online, ultima_atividade, 
                           modo_status
                    FROM users
                    WHERE id = %s
                """, (usuario_id,))
                usuario = cursor.fetchone()

                # ESTATISTICA DO USUARIO
                cursor.execute("""
                    SELECT
                        (SELECT COUNT(*) FROM posts WHERE users_id = %s) AS total_posts,
                        (SELECT COUNT(*) FROM curtidas WHERE post_id IN (SELECT id FROM posts WHERE users_id = %s)) AS total_curtidas,
                        (SELECT COUNT(*) FROM posts_republicados WHERE post_id IN (SELECT id FROM posts WHERE users_id = %s)) AS total_republicacoes,
                        (SELECT COUNT(*) FROM posts_salvos WHERE post_id IN (SELECT id FROM posts WHERE users_id = %s)) AS total_salvos,
                        (SELECT COUNT(*) FROM curtidas WHERE usuario_id = %s) AS total_posts_que_curti,
                        (SELECT COUNT(*) FROM posts_republicados WHERE usuario_id = %s) AS total_posts_que_republiquei,
                        (SELECT COUNT(*) FROM posts_salvos WHERE usuario_id = %s) AS total_posts_que_salvei,
                        (SELECT COUNT(*) FROM comentarios WHERE post_id IN (SELECT id FROM posts WHERE users_id = %s)) AS total_comentarios,
                        (SELECT COUNT(*) FROM visualizacoes WHERE post_id IN (SELECT id FROM posts WHERE users_id = %s)) AS total_visualizacoes,
                        (SELECT COUNT(*) FROM comentarios WHERE usuario_id = %s) AS total_comentarios_feitos
                """, (usuario_id, usuario_id, usuario_id, usuario_id,
                    usuario_id, usuario_id, usuario_id, usuario_id,
                    usuario_id, usuario_id))

                estatisticas = cursor.fetchone()

                if usuario:
                    nome_completo = usuario['nome']
                    nome_usuario = usuario['username']
                    foto_perfil = usuario['fotos_perfil'] if usuario['fotos_perfil'] else url_for('static', filename='img/icone/user.png')
                    bio_user = usuario['bio']
                    foto_capa = usuario['foto_capa'] if usuario['foto_capa'] else url_for('static', filename='img/icone/redes-sociais-capa-1.jpg')
                    
                    # PERFIL PUBLICO
                    perfil_publico = bool(usuario['perfil_publico']) if usuario['perfil_publico'] is not None else True

                    # COMENTARIO (PUBLICO, PRIVADO, AMIOS)
                    comentarios_publicos = usuario['comentarios_publicos'] if usuario['comentarios_publicos'] is not None else 'todos'

                    visibilidade_seguidores = usuario['visibilidade_seguidores'] if usuario['visibilidade_seguidores'] else 'publico'
                    tema = usuario.get('tema', 'claro')

                    curtidas_publicas = usuario.get('curtidas_publicas')
                    if curtidas_publicas is None:
                        curtidas_publicas = True
                    else:
                        curtidas_publicas = bool(curtidas_publicas)

                    audio_notificacoes = usuario.get('audio_notificacoes')
                    if audio_notificacoes is None:
                        audio_notificacoes = True
                    else:
                        audio_notificacoes = bool(audio_notificacoes)

                    audio_notificacoes_mensagem = usuario.get('audio_notificacoes_mensagem')
                    if audio_notificacoes_mensagem is None:
                        audio_notificacoes_mensagem = True
                    else:
                        audio_notificacoes_mensagem = bool(audio_notificacoes_mensagem)

                    codigo_user = usuario.get('codigo_user')
                    online = usuario.get('online', 0)
                    ultima_atividade = usuario.get('ultima_atividade')
                    modo_status = usuario.get('modo_status', 'normal')
                else:
                    nome_completo = None
                    nome_usuario = None
                    foto_perfil = url_for('static', filename='img/icone/user.png')
                    bio_user = None
                    foto_capa = url_for('static', filename='img/icone/redes-sociais-capa-1.jpg')
                    perfil_publico = True
                    comentarios_publicos = 'todos'
                    visibilidade_seguidores = 'publico'
                    tema = 'claro'
                    curtidas_publicas = True
                    audio_notificacoes = True
                    audio_notificacoes_mensagem = True
                    codigo_user = None
                    online = 0
                    ultima_atividade = None
                    modo_status = 'normal'

                # HASHTAG DO MOMENTO
                hashtags_top = buscar_hashtags_mais_usadas(cursor)

            conexao.close()

            return render_template('configuracao.html',
                                   nome=nome_completo,
                                   username=nome_usuario,
                                   foto_perfil=foto_perfil,
                                   bio=bio_user,
                                   foto_capa=foto_capa,
                                   perfil_publico=perfil_publico,
                                   comentarios_publicos=comentarios_publicos,
                                   visibilidade_seguidores=visibilidade_seguidores,
                                   tema=tema,
                                   claro=(tema == 'claro'),
                                   curtidas_publicas=curtidas_publicas,
                                   audio_notificacoes=audio_notificacoes,
                                   audio_notificacoes_mensagem=audio_notificacoes_mensagem,
                                   codigo_user=codigo_user,
                                   online=online,
                                   ultima_atividade=ultima_atividade,
                                   modo_status=modo_status,
    total_posts=estatisticas['total_posts'],
    total_curtidas=estatisticas['total_curtidas'],
    total_republicacoes=estatisticas['total_republicacoes'],
    total_salvos=estatisticas['total_salvos'],
    total_posts_que_curti=estatisticas['total_posts_que_curti'],
    total_posts_que_republiquei=estatisticas['total_posts_que_republiquei'],
    total_posts_que_salvei=estatisticas['total_posts_que_salvei'],
    total_comentarios=estatisticas['total_comentarios'],
    total_visualizacoes=estatisticas['total_visualizacoes'],
    total_comentarios_feitos=estatisticas['total_comentarios_feitos'],
                                   hashtags_top=hashtags_top)
        else:
            return "Erro na conexão com o banco de dados."

    except Exception as e:
        return f"Erro ao conectar ao banco de dados. Detalhes: {str(e)}"
# =============================================================
#  MUDAR TEMA PARA CLARO OU ESCURO
# =============================================================
@configuracao_bp.route('/alterar_tema', methods=['POST'])
def alterar_tema():
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    try:
        data = request.get_json()
        usuario_id = session['usuario_id']
        tema = data.get('tema', 'escuro')  

        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
                cursor.execute("UPDATE users SET tema = %s WHERE id = %s", (tema, usuario_id))
                conexao.commit()
            conexao.close()
            return jsonify({
                'message': 'Tema atualizado com sucesso!',
                'tema': tema,
                'redirect_url': url_for('configuracao.configuracao')
            })
        else:
            return jsonify({'error': 'Erro na conexão com o banco de dados.'}), 500

    except Exception as e:
        return jsonify({'error': f'Erro ao atualizar tema. Detalhes: {str(e)}'}), 500
# =============================================
#  AQUI FAZ DEIXAR O PERFIL PUBLICO OU PRIVADO
# =============================================   
@configuracao_bp.route('/alterar_visibilidade', methods=['POST'])
def alterar_visibilidade():
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    try:
        data = request.get_json()
        usuario_id = session['usuario_id']
        perfil_publico = data.get('perfil_publico', False)

        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:

                # PRIMEIRO BUSCAR O VALOR ATUAL
                cursor.execute("SELECT perfil_publico FROM users WHERE id = %s", (usuario_id,))
                resultado = cursor.fetchone()
                perfil_publico_atual = resultado['perfil_publico'] if resultado else None

                # ATUALIZA O CAMPO
                cursor.execute("UPDATE users SET perfil_publico = %s WHERE id = %s", 
                               (perfil_publico, usuario_id))
                
                # SE ESTAVA PRIVADO E FOI ARA PUBLICO APAGA OS PEDIDOS
                if perfil_publico_atual == 0 and perfil_publico:
                    cursor.execute("""
                        DELETE FROM pedidos_seguir WHERE id_destino = %s
                    """, (usuario_id,))

                conexao.commit()
            conexao.close()
            
            return jsonify({
                'message': 'Visibilidade do perfil atualizada com sucesso!',
                'perfil_publico': perfil_publico
            })
        else:
            return jsonify({'error': 'Erro na conexão com o banco de dados'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500
# ==================================================
#  AQUI FAZ DEIXAR OS COMENTARIOS PUBLICO OU PRIVADO
# ==================================================
@configuracao_bp.route('/alterar_visibilidade_comentarios', methods=['POST'])
def alterar_visibilidade_comentarios():
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    try:
        data = request.get_json()
        usuario_id = session['usuario_id']
        comentarios_publicos = data.get('comentarios_publicos', 'todos') 

        if comentarios_publicos not in ('todos', 'privado', 'seguidores_mutuos'):
            return jsonify({'error': 'Valor inválido para comentarios_publicos'}), 400

        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
                cursor.execute("UPDATE users SET comentarios_publicos = %s WHERE id = %s", 
                               (comentarios_publicos, usuario_id))
                conexao.commit()
            conexao.close()
            return jsonify({
                'message': 'Configuração de comentários atualizada com sucesso!',
                'comentarios_publicos': comentarios_publicos
            })
        else:
            return jsonify({'error': 'Erro na conexão com o banco de dados'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500
# =============================================================
#  PERMITI QUE O USUARIO POSSA VER O MODAL DE SEGUIDORES OU NAO
# =============================================================
@configuracao_bp.route('/alterar_visibilidade_seguidores', methods=['POST'])
def alterar_visibilidade_seguidores():
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    try:
        data = request.get_json()
        usuario_id = session['usuario_id']
        visibilidade_seguidores = data.get('visibilidade_seguidores')

        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
                cursor.execute("UPDATE users SET visibilidade_seguidores = %s WHERE id = %s", 
                              (visibilidade_seguidores, usuario_id))
                conexao.commit()
            conexao.close()
            return jsonify({
                'message': 'Visibilidade dos seguidores atualizada com sucesso!',
                'visibilidade_seguidores': visibilidade_seguidores
            })
        else:
            return jsonify({'error': 'Erro na conexão com o banco de dados.'}), 500

    except Exception as e:
        return jsonify({'error': f'Erro ao atualizar a visibilidade dos seguidores. Detalhes: {str(e)}'}), 500
# =============================================================
#  PESQUISAR USUARIOS
# =============================================================
@configuracao_bp.route('/pesquisar_usuarios', methods=['POST'])
def pesquisar_usuarios():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    termo = request.form.get('termo', '')
    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:

                # PESQUISAR USER
                cursor.execute("""
                    SELECT id, nome, username, fotos_perfil 
                    FROM users 
                    WHERE (nome LIKE %s OR username LIKE %s) 
                    AND id != %s
                    LIMIT 10
                """, (f'%{termo}%', f'%{termo}%', usuario_id))
                usuarios = cursor.fetchall()

                # VERIFICA QUAIS ESTAO BLOQUEADOS
                cursor.execute("""
                    SELECT bloqueado_id 
                    FROM bloqueados 
                    WHERE usuario_id = %s
                """, (usuario_id,))
                bloqueados = [row['bloqueado_id'] for row in cursor.fetchall()]

                for usuario in usuarios:
                    usuario['ja_bloqueado'] = usuario['id'] in bloqueados
                    usuario['foto_perfil'] = usuario['fotos_perfil'] if usuario['fotos_perfil'] else url_for('static', filename='img/icone/user.png')

            conexao.close()
            return json.dumps(usuarios)
        else:
            return json.dumps({'error': 'Erro na conexão com o banco de dados'})

    except Exception as e:
        return json.dumps({'error': str(e)})
# =============================================================
#  BLOQUEAR USER
# =============================================================
@configuracao_bp.route('/bloquear_usuario', methods=['POST'])
def bloquear_usuario():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']
    bloqueado_id = request.form.get('bloqueado_id')

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
                # REMOVER SE AMBOS SE SEGUEM
                cursor.execute("""
                    DELETE FROM seguindo 
                    WHERE (id_seguidor = %s AND id_seguindo = %s)
                    OR (id_seguidor = %s AND id_seguindo = %s)
                """, (usuario_id, bloqueado_id, bloqueado_id, usuario_id))

                # REMOVE CURTIDAS QUE EU DEI NOS POSTS DELE
                cursor.execute("""
                    DELETE c FROM curtidas c
                    JOIN posts p ON c.post_id = p.id
                    WHERE c.usuario_id = %s AND p.users_id = %s
                """, (usuario_id, bloqueado_id))

                # REMOVE CURTIDAS QUE ELE DEU NOS MEUS POSTS
                cursor.execute("""
                    DELETE c FROM curtidas c
                    JOIN posts p ON c.post_id = p.id
                    WHERE c.usuario_id = %s AND p.users_id = %s
                """, (bloqueado_id, usuario_id))

                # REMOVE REPUBLICAÇÕES FEITAS POR MIM DOS POSTS DELE
                cursor.execute("""
                    DELETE pr FROM posts_republicados pr
                    JOIN posts p ON pr.post_id = p.id
                    WHERE pr.usuario_id = %s AND p.users_id = %s
                """, (usuario_id, bloqueado_id))

                # REMOVE REPUBLICAÇÕES QUE ELE FEZ DOS MEUS POSTS
                cursor.execute("""
                    DELETE pr FROM posts_republicados pr
                    JOIN posts p ON pr.post_id = p.id
                    WHERE pr.usuario_id = %s AND p.users_id = %s
                """, (bloqueado_id, usuario_id))

                # REMOVE SALVOS FEITOS POR MIM DOS POSTS DELE
                cursor.execute("""
                    DELETE ps FROM posts_salvos ps
                    JOIN posts p ON ps.post_id = p.id
                    WHERE ps.usuario_id = %s AND p.users_id = %s
                """, (usuario_id, bloqueado_id))

                # REMOVE SALVOS QUE ELE FEZ DOS MEUS POSTS
                cursor.execute("""
                    DELETE ps FROM posts_salvos ps
                    JOIN posts p ON ps.post_id = p.id
                    WHERE ps.usuario_id = %s AND p.users_id = %s
                """, (bloqueado_id, usuario_id))

                # ADICIONA À LISTA DE BLOQUEADOS
                cursor.execute("""
                    INSERT INTO bloqueados (usuario_id, bloqueado_id) 
                    VALUES (%s, %s)
                """, (usuario_id, bloqueado_id))

                conexao.commit()
            conexao.close()
            return json.dumps({'success': True})
        else:
            return json.dumps({'error': 'Erro na conexão com o banco de dados'})
    except Exception as e:
        return json.dumps({'error': str(e)})
# =============================================================
#  BLOQUEAR USER VIA POST
# =============================================================
@configuracao_bp.route('/bloquear_usuario_via_post', methods=['POST'])
def bloquear_usuario_via_post():
    if 'usuario_id' not in session:
        flash('Você precisa estar logado para bloquear usuários', 'error')
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']
    bloqueado_id = request.form.get('bloqueado_id')

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:

                # REMOVE SE ALGUEM SE SEGUI
                cursor.execute("""
                    DELETE FROM seguindo 
                    WHERE (id_seguidor = %s AND id_seguindo = %s)
                    OR (id_seguidor = %s AND id_seguindo = %s)
                """, (usuario_id, bloqueado_id, bloqueado_id, usuario_id))

                # REMOVE AS CURTIDAS QUE EU DEI NO POST DELE
                cursor.execute("""
                    DELETE c FROM curtidas c
                    JOIN posts p ON c.post_id = p.id
                    WHERE c.usuario_id = %s AND p.users_id = %s
                """, (usuario_id, bloqueado_id))

                # REMOVE AS CURTIDAS QUE ELE DEU NO MEU POST
                cursor.execute("""
                    DELETE c FROM curtidas c
                    JOIN posts p ON c.post_id = p.id
                    WHERE c.usuario_id = %s AND p.users_id = %s
                """, (bloqueado_id, usuario_id))

                # REMOVE AS REPUBLICAÇOES DELE DOS MEU POST
                cursor.execute("""
                    DELETE pr FROM posts_republicados pr
                    JOIN posts p ON pr.post_id = p.id
                    WHERE pr.usuario_id = %s AND p.users_id = %s
                """, (bloqueado_id, usuario_id))

                # REMOVE AS REPUBLICAÇOES QUE EU FIZ DO POST DELE
                cursor.execute("""
                    DELETE pr FROM posts_republicados pr
                    JOIN posts p ON pr.post_id = p.id
                    WHERE pr.usuario_id = %s AND p.users_id = %s
                """, (usuario_id, bloqueado_id))

                # REMOVE OS SALVOS QUE EU FIZ NO POST DELE
                cursor.execute("""
                    DELETE ps FROM posts_salvos ps
                    JOIN posts p ON ps.post_id = p.id
                    WHERE ps.usuario_id = %s AND p.users_id = %s
                """, (usuario_id, bloqueado_id))

                # REMOVE OS SALVOS QU ELE FEZ NO MEU POST
                cursor.execute("""
                    DELETE ps FROM posts_salvos ps
                    JOIN posts p ON ps.post_id = p.id
                    WHERE ps.usuario_id = %s AND p.users_id = %s
                """, (bloqueado_id, usuario_id))

                # ADICIONA A LISTA DE BLOQUEADOS
                cursor.execute("""
                    INSERT INTO bloqueados (usuario_id, bloqueado_id) 
                    VALUES (%s, %s)
                """, (usuario_id, bloqueado_id))

                conexao.commit()
            conexao.close()
            flash('Usuário bloqueado com sucesso!', 'success')
        else:
            flash('Erro ao conectar ao banco de dados', 'error')

    except Exception as e:
        flash(f'Erro ao bloquear usuário: {str(e)}', 'error')

    next_url = request.form.get('next') or request.referrer or url_for('home.home')
    return redirect(next_url)
# =============================================================
#  DESBLOQUEAR USUARIO
# =============================================================
@configuracao_bp.route('/desbloquear_usuario', methods=['POST'])
def desbloquear_usuario():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']
    bloqueado_id = request.form.get('bloqueado_id')

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM bloqueados 
                    WHERE usuario_id = %s AND bloqueado_id = %s
                """, (usuario_id, bloqueado_id))
                conexao.commit()
            conexao.close()
            return json.dumps({'success': True})
        else:
            return json.dumps({'error': 'Erro na conexão com o banco de dados'})

    except Exception as e:
        return json.dumps({'error': str(e)})
# =============================================================
#  DESBLOQUEAR USUARIO PELO PERFIL
# =============================================================
@configuracao_bp.route('/desbloquear_usuario_via_perfil', methods=['POST'])
def desbloquear_usuario_via_perfil():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']
    bloqueado_id = request.form.get('bloqueado_id')

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM bloqueados 
                    WHERE usuario_id = %s AND bloqueado_id = %s
                """, (usuario_id, bloqueado_id))
                conexao.commit()
            conexao.close()
            flash('Usuário desbloqueado com sucesso!', 'success')
        else:
            flash('Erro ao conectar ao banco de dados.', 'error')
    except Exception as e:
        flash(f'Erro ao desbloquear usuário: {str(e)}', 'error')

    return redirect(url_for('info_user.info_user', id_usuario=bloqueado_id))
# =============================================================
#  LISTA DE USUARIOS BLOQUEADOS
# =============================================================
@configuracao_bp.route('/listar_bloqueados')
def listar_bloqueados():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT u.id, u.nome, u.username, u.fotos_perfil 
                    FROM users u
                    JOIN bloqueados b ON u.id = b.bloqueado_id
                    WHERE b.usuario_id = %s
                """, (usuario_id,))
                bloqueados = cursor.fetchall()

                for bloqueado in bloqueados:
                    bloqueado['foto_perfil'] = bloqueado['fotos_perfil'] if bloqueado['fotos_perfil'] else url_for('static', filename='img/icone/user.png')

            conexao.close()
            return json.dumps(bloqueados)
        else:
            return json.dumps({'error': 'Erro na conexão com o banco de dados'})

    except Exception as e:
        return json.dumps({'error': str(e)})
# =============================================================
#  DEIXA O MODAL DE CURTIDAS PUBLICOS OU PRIVADOS
# =============================================================
@configuracao_bp.route('/alterar_curtidas_publicas', methods=['POST'])
def alterar_curtidas_publicas():
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401

    try:
        data = request.get_json()
        usuario_id = session['usuario_id']
        valor = data.get('curtidas_publicas', 'publico')
        curtidas_publicas = valor == 'publico'

        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
                cursor.execute("UPDATE users SET curtidas_publicas = %s WHERE id = %s", (curtidas_publicas, usuario_id))
                conexao.commit()
            conexao.close()
            return jsonify({
                'message': 'Configuração de curtidas atualizada com sucesso!',
                'curtidas_publicas': curtidas_publicas
            })
        else:
            return jsonify({'error': 'Erro na conexão com o banco de dados.'}), 500

    except Exception as e:
        return jsonify({'error': f'Erro ao atualizar curtidas. Detalhes: {str(e)}'}), 500
# =========================================================================
#  PERMITI OU NAO O SOM DE NOTIFICAÇÃO DE NOVA MENSAGEM QUANDO ESTA NO CHAT
# ==========================================================================
@configuracao_bp.route('/alterar_audio_notificacoes_mensagem', methods=['POST'])
def alterar_audio_notificacoes_mensagem():
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    try:
        data = request.get_json()
        usuario_id = session['usuario_id']
        valor = data.get('audio_notificacoes_mensagem', 'ativado') 
        audio_notificacoes_mensagem = valor == 'ativado'  

        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
                cursor.execute(
                    "UPDATE users SET audio_notificacoes_mensagem = %s WHERE id = %s",
                    (audio_notificacoes_mensagem, usuario_id)
                )
                conexao.commit()
            conexao.close()
            return jsonify({
                'message': 'Configuração de notificações de áudio para mensagens atualizada com sucesso!',
                'audio_notificacoes_mensagem': audio_notificacoes_mensagem
            })
        else:
            return jsonify({'error': 'Erro na conexão com o banco de dados.'}), 500
    except Exception as e:
        return jsonify({'error': f'Erro ao atualizar notificações de áudio para mensagens. Detalhes: {str(e)}'}), 500
# =============================================================
#  PERMITIR QUE O USER DEIXA O STATUS ON/OFF OU AUSENTE
# =============================================================
@configuracao_bp.route('/alterar_modo_status', methods=['POST'])
def alterar_modo_status():
    if 'usuario_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    try:
        data = request.get_json()
        usuario_id = session['usuario_id']
        modo_status = data.get('modo_status', 'normal')
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
                cursor.execute("UPDATE users SET modo_status = %s WHERE id = %s", (modo_status, usuario_id))
                conexao.commit()
            conexao.close()
            return jsonify({'message': 'Modo de status atualizado com sucesso!'})
        else:
            return jsonify({'error': 'Erro na conexão com o banco de dados.'}), 500
    except Exception as e:
        return jsonify({'error': f'Erro ao atualizar modo de status. Detalhes: {str(e)}'}), 500
# =============================================================
#  ALTERAR SENHA 
# =============================================================
@configuracao_bp.route('/alterar_senha', methods=['POST'])
def alterar_senha():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401

    try:
        data = request.get_json()
        usuario_id = session['usuario_id']
        senha_atual = data.get('senha_atual')
        nova_senha = data.get('nova_senha')
        confirmar_senha = data.get('confirmar_senha')

        if not all([senha_atual, nova_senha, confirmar_senha]):
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'}), 400

        if nova_senha != confirmar_senha:
            return jsonify({'success': False, 'message': 'As novas senhas não coincidem'}), 400

        if len(nova_senha) < 6:
            return jsonify({'success': False, 'message': 'A nova senha deve ter no mínimo 6 caracteres'}), 400

        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT senha FROM users WHERE id = %s", (usuario_id,))
                usuario = cursor.fetchone()

                if not usuario:
                    return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404

                if not check_password_hash(usuario['senha'], senha_atual):
                    return jsonify({'success': False, 'message': 'Senha atual incorreta'}), 401

                nova_hash = generate_password_hash(nova_senha)
                cursor.execute("UPDATE users SET senha = %s WHERE id = %s", 
                               (nova_hash, usuario_id))
                conexao.commit()

            conexao.close()
            return jsonify({'success': True, 'message': 'Senha alterada com sucesso!'})

        else:
            return jsonify({'success': False, 'message': 'Erro na conexão com o banco de dados'}), 500

    except Exception as e:
        return jsonify({'success': False, 'message': f'Erro ao alterar senha: {str(e)}'}), 500
# =============================================================
#  APAGAR CONTA
# =============================================================
@configuracao_bp.route('/excluir_conta', methods=['POST'])
def excluir_conta():  
    if 'usuario_id' not in session:
        return jsonify(success=False, message="Usuário não autenticado."), 401

    usuario_id = session['usuario_id']
    dados = request.get_json()
    if dados:
        senha = dados.get('senha')
        confirmar_senha = dados.get('confirmarSenhaExcluir')
    else:
        senha = request.form.get('senha')
        confirmar_senha = request.form.get('confirmarSenhaExcluir')

    if not senha or not confirmar_senha:
        return jsonify(success=False, message="Preencha todos os campos de senha."), 400

    if senha != confirmar_senha:
        return jsonify(success=False, message="As senhas não coincidem."), 400

    try:
        conexao = criar_conexao()
        with conexao.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT senha FROM users WHERE id = %s", (usuario_id,))
            user = cursor.fetchone()

            if not user or not check_password_hash(user['senha'], senha):
                return jsonify(success=False, message="Senha incorreta."), 400

            tabelas_colunas = {
                'comentario_mencoes': ['user_mencionado_id'],
                'comentarios': ['usuario_id'],
                'curtidas': ['usuario_id'],
                'mensagens': ['id_remetente', 'id_destinatario'],
                'notificacoes': ['usuario_id', 'origem_usuario_id'],
                'pedidos_seguir': ['id_solicitante', 'id_destino'],
                'historico_pesquisa_post': ['usuario_id'],
                'historico_pesquisa_procurar_usuarios': ['usuario_id', 'usuario_pesquisado_id'],
                'recuperacao_senha': ['user_id'],
                'posts_republicados': ['usuario_id'],
                'posts_salvos': ['usuario_id'],
                'visualizacoes': ['usuario_id'],
                'visualizacoes_perfis': ['usuario_id'],
                'seguindo': ['id_seguidor', 'id_seguindo'],
                'pesquisas': ['usuario_id'],
                'denuncias': ['id_denunciante'],
                # posts será tratado depois
            }

            # APAGA OS REGISTRO DO USER
            for tabela, colunas in tabelas_colunas.items():
                for coluna in colunas:
                    try:
                        cursor.execute(f"DELETE FROM {tabela} WHERE {coluna} = %s", (usuario_id,))
                    except Exception as e:
                        print(f"Erro ao deletar {tabela}.{coluna}: {e}")

            # APAGA AS MENÇOES ONDE O USER E MENCIONADO
            try:
                cursor.execute("DELETE FROM post_mencoes WHERE user_mencionado_id = %s", (usuario_id,))
            except Exception as e:
                print(f"Erro ao deletar post_mencoes (user_mencionado_id): {e}")

            # APAGA AS MENÇOES DO POST
            try:
                cursor.execute("""
                    DELETE pm FROM post_mencoes pm
                    JOIN posts p ON pm.post_id = p.id
                    WHERE p.users_id = %s
                """, (usuario_id,))
            except Exception as e:
                print(f"Erro ao deletar post_mencoes ligados aos posts: {e}")

            # APAGA OS POST
            try:
                cursor.execute("DELETE FROM posts WHERE users_id = %s", (usuario_id,))
            except Exception as e:
                print(f"Erro ao deletar posts do usuário: {e}")

            # APAGA O USER
            cursor.execute("DELETE FROM users WHERE id = %s", (usuario_id,))

            conexao.commit()
            session.clear()

            return jsonify(success=True, message="Sua conta foi excluída com sucesso.")

    except Exception as e:
        print("Erro ao excluir conta:", e)
        return jsonify(success=False, message="Erro interno ao excluir a conta."), 500
