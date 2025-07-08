from flask import Blueprint, render_template, redirect, url_for, session, request, flash, json, jsonify
from werkzeug.utils import secure_filename
from app.conexao import criar_conexao
from datetime import datetime

configuracao_bp = Blueprint('configuracao', __name__)


@configuracao_bp.route('/configuracao')
def configuracao():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Busca todos os campos relevantes para configurações, incluindo modo_status
                cursor.execute("""
                    SELECT nome, username, fotos_perfil, bio, foto_capa, perfil_publico, comentarios_publicos, visibilidade_seguidores, tema,
                           curtidas_publicas, audio_notificacoes, audio_notificacoes_mensagem, codigo_user, online, ultima_atividade, 
                           modo_status
                    FROM users
                    WHERE id = %s
                """, (usuario_id,))
                usuario = cursor.fetchone()

                # Garante valores default para campos que podem ser None
                if usuario:
                    nome_completo = usuario['nome']
                    nome_usuario = usuario['username']
                    foto_perfil = usuario['fotos_perfil'] if usuario['fotos_perfil'] else url_for('static', filename='img/icone/user.png')
                    bio_user = usuario['bio']
                    foto_capa = usuario['foto_capa'] if usuario['foto_capa'] else url_for('static', filename='img/icone/redes-sociais-capa-1.jpg')
                    perfil_publico = usuario['perfil_publico'] if usuario['perfil_publico'] is not None else True
                    comentarios_publicos = usuario['comentarios_publicos'] if usuario['comentarios_publicos'] is not None else True
                    visibilidade_seguidores = usuario['visibilidade_seguidores'] if usuario['visibilidade_seguidores'] else 'publico'
                    tema = usuario.get('tema', 'claro')
                    curtidas_publicas = usuario.get('curtidas_publicas')
                    if curtidas_publicas is None:
                        curtidas_publicas = True
                    audio_notificacoes = usuario.get('audio_notificacoes')
                    if audio_notificacoes is None:
                        audio_notificacoes = True
                    audio_notificacoes_mensagem = usuario.get('audio_notificacoes_mensagem')
                    if audio_notificacoes_mensagem is None:
                        audio_notificacoes_mensagem = True
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
                    comentarios_publicos = True
                    visibilidade_seguidores = 'publico'
                    tema = 'claro'
                    curtidas_publicas = True
                    audio_notificacoes = True
                    audio_notificacoes_mensagem = True
                    codigo_user = None
                    online = 0
                    ultima_atividade = None
                    modo_status = 'normal'

                # Buscar as 3 hashtags mais usadas nas últimas 10 horas
                cursor.execute("""
                    SELECT h.nome, COUNT(*) as total
                    FROM hashtags h
                    JOIN post_hashtags ph ON h.id = ph.hashtag_id
                    JOIN posts p ON ph.post_id = p.id
                    WHERE p.data_postagem >= NOW() - INTERVAL 10 HOUR
                    GROUP BY h.id, h.nome
                    ORDER BY total DESC
                    LIMIT 3
                """)
                hashtags_top = cursor.fetchall()

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
                                 hashtags_top=hashtags_top,
                               )
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
        tema = data.get('tema', 'escuro')  # espera 'claro' ou 'escuro'

        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
                cursor.execute("UPDATE users SET tema = %s WHERE id = %s", (tema, usuario_id))
                conexao.commit()
            conexao.close()
            # Adiciona a URL para redirecionamento no JSON
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
            with conexao.cursor() as cursor:
                cursor.execute("UPDATE users SET perfil_publico = %s WHERE id = %s", 
                             (perfil_publico, usuario_id))
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
        comentarios_publicos = int(data.get('comentarios_publicos', 0))

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

# ==================
# PESQUISAR USUARIOS
# ==================
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
                # Pesquisa usuários que correspondam ao termo (nome ou username)
                cursor.execute("""
                    SELECT id, nome, username, fotos_perfil 
                    FROM users 
                    WHERE (nome LIKE %s OR username LIKE %s) 
                    AND id != %s
                    LIMIT 10
                """, (f'%{termo}%', f'%{termo}%', usuario_id))
                usuarios = cursor.fetchall()

                # Verifica quais usuários já estão bloqueados
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

# ==================
#  BLOQUEAR USUARIOS
# ==================
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
                # Remove any following relationships in both directions
                cursor.execute("""
                    DELETE FROM seguindo 
                    WHERE (id_seguidor = %s AND id_seguindo = %s)
                    OR (id_seguidor = %s AND id_seguindo = %s)
                """, (usuario_id, bloqueado_id, bloqueado_id, usuario_id))

                                # Remove curtidas que VOCÊ deu nos posts dele
                cursor.execute("""
                    DELETE c FROM curtidas c
                    JOIN posts p ON c.post_id = p.id
                    WHERE c.usuario_id = %s AND p.users_id = %s
                """, (usuario_id, bloqueado_id))

                # Remove curtidas que ELE deu nos seus posts
                cursor.execute("""
                    DELETE c FROM curtidas c
                    JOIN posts p ON c.post_id = p.id
                    WHERE c.usuario_id = %s AND p.users_id = %s
                """, (bloqueado_id, usuario_id))
                                
                # Add to blocked list
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

# ==================
#  BLOQUEAR USUARIOS
# ==================   
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
                # Remove relações de seguir em ambas as direções
                cursor.execute("""
                    DELETE FROM seguindo 
                    WHERE (id_seguidor = %s AND id_seguindo = %s)
                    OR (id_seguidor = %s AND id_seguindo = %s)
                """, (usuario_id, bloqueado_id, bloqueado_id, usuario_id))

                cursor.execute("""
                    DELETE c FROM curtidas c
                    JOIN posts p ON c.post_id = p.id
                    WHERE c.usuario_id = %s AND p.users_id = %s
                """, (usuario_id, bloqueado_id))

                # Remove curtidas que ELE deu nos seus posts
                cursor.execute("""
                    DELETE c FROM curtidas c
                    JOIN posts p ON c.post_id = p.id
                    WHERE c.usuario_id = %s AND p.users_id = %s
                """, (bloqueado_id, usuario_id))
                
                # Adiciona à lista de bloqueados
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

# =====================
#  DESBLOQUEAR USUARIOS
# =====================
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

# =====================
#  DESBLOQUEAR USUARIOS
# =====================
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

    # Redireciona de volta para o perfil do usuário desbloqueado
    return redirect(url_for('info_user.info_user', id_usuario=bloqueado_id))

# =============================
#  LISTA DE USUARIOS BLOQUEADOS
# =============================
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
    
# ===============================================
#  ALTERA SE AS CURTIDAS SÃO PÚBLICAS OU PRIVADAS
# ===============================================
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
        valor = data.get('audio_notificacoes_mensagem', 'ativado')  # espera 'ativado' ou 'desativado'
        audio_notificacoes_mensagem = valor == 'ativado'  # True se 'ativado', False caso contrário

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
    
# =====================================================
#  PERMITI QUE USUARIO DEIXE O STATUS ON/OFF OU AUSENTE
# =====================================================
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

        # Validações básicas
        if not all([senha_atual, nova_senha, confirmar_senha]):
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'}), 400

        if nova_senha != confirmar_senha:
            return jsonify({'success': False, 'message': 'As novas senhas não coincidem'}), 400

        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Verifica a senha atual (sem hash)
                cursor.execute("SELECT senha FROM users WHERE id = %s", (usuario_id,))
                usuario = cursor.fetchone()

                if not usuario:
                    return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404

                # Comparação direta da senha (sem hash)
                if senha_atual != usuario['senha']:
                    return jsonify({'success': False, 'message': 'Senha atual incorreta'}), 401

                # Atualiza a senha (sem hash)
                cursor.execute("UPDATE users SET senha = %s WHERE id = %s", 
                             (nova_senha, usuario_id))
                conexao.commit()
            
            conexao.close()
            return jsonify({
                'success': True,
                'message': 'Senha alterada com sucesso!'
            })
        else:
            return jsonify({'success': False, 'message': 'Erro na conexão com o banco de dados'}), 500

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Erro ao alterar senha: {str(e)}'
        }), 500