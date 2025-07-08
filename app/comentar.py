from flask import Blueprint, request, session, jsonify
from app.utils import extrair_mencoes, replace_mentions_comentario, formatar_data
from app.conexao import criar_conexao
from datetime import datetime
from markupsafe import Markup
import re

comentar_bp = Blueprint('comentar', __name__)

@comentar_bp.route('/comentar/<int:post_id>', methods=['POST'])
def comentar(post_id):
    if 'usuario_id' not in session:
        return jsonify(success=False, error="Usuário não está logado"), 403

    usuario_id = session['usuario_id']
    comentario = request.form['comentario']
    parent_comment_id = request.form.get('parent_comment_id', None)

    if not comentario:
        return jsonify(success=False, error="Comentário vazio"), 400

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Verifica as configurações de comentários do dono do post
                cursor.execute("""
                    SELECT p.users_id, u.comentarios_publicos 
                    FROM posts p
                    JOIN users u ON p.users_id = u.id
                    WHERE p.id = %s
                """, (post_id,))
                post_info = cursor.fetchone()
                
                if not post_info:
                    return jsonify(success=False, error="Post não encontrado"), 404
                
                # Se os comentários não são públicos E o usuário não é o dono do post
                if post_info['comentarios_publicos'] == 0 and usuario_id != post_info['users_id']:
                    return jsonify(success=False, error="Comentários estão desativados para este post"), 403

                # Insere o comentário
                cursor.execute("""
                    INSERT INTO comentarios (post_id, usuario_id, comentario, parent_comment_id) 
                    VALUES (%s, %s, %s, %s)
                """, (post_id, usuario_id, comentario, parent_comment_id))

                comentario_id = cursor.lastrowid

                # --- MENÇÕES EM COMENTÁRIOS ---
                mencoes = extrair_mencoes(comentario)
                for username in mencoes:
                    cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                    resultado = cursor.fetchone()
                    if resultado:
                        mencionado_id = resultado['id']
                        if mencionado_id != usuario_id:
                            cursor.execute("""
                                INSERT INTO notificacoes (usuario_id, tipo, origem_usuario_id, post_id, comentario_id, lida)
                                VALUES (%s, 'mencao', %s, %s, %s, 0)
                            """, (mencionado_id, usuario_id, post_id, comentario_id))
                # --- FIM MENÇÕES ---

                # Notificações padrão
                cursor.execute("""
                    SELECT users_id FROM posts WHERE id = %s
                """, (post_id,))
                post_owner_id = cursor.fetchone()['users_id']

                # Notifica o dono do post se não for o próprio usuário E NÃO for resposta (parent_comment_id)
                if usuario_id != post_owner_id and not parent_comment_id:
                    cursor.execute("""
                        INSERT INTO notificacoes (usuario_id, tipo, origem_usuario_id, post_id, comentario_id)
                        VALUES (%s, 'comentario', %s, %s, %s)
                    """, (post_owner_id, usuario_id, post_id, comentario_id))

                # Se for resposta, notifica o dono do comentário pai (sempre, exceto se for o próprio usuário)
                parent_username = None
                parent_usuario_id = None
                if parent_comment_id:
                    cursor.execute("""
                        SELECT usuario_id FROM comentarios WHERE id = %s
                    """, (parent_comment_id,))
                    parent_comment_owner = cursor.fetchone()
                    if parent_comment_owner:
                        parent_owner_id = parent_comment_owner['usuario_id']
                        if parent_owner_id != usuario_id:
                            cursor.execute("""
                                INSERT INTO notificacoes (usuario_id, tipo, origem_usuario_id, post_id, comentario_id)
                                VALUES (%s, 'resposta', %s, %s, %s)
                            """, (parent_owner_id, usuario_id, post_id, comentario_id))
                    # Pega username/id do comentário pai
                    cursor.execute("""
                        SELECT u.username, u.id as usuario_id 
                        FROM comentarios c
                        JOIN users u ON c.usuario_id = u.id
                        WHERE c.id = %s
                    """, (parent_comment_id,))
                    parent_result = cursor.fetchone()
                    if parent_result:
                        parent_username = parent_result['username']
                        parent_usuario_id = parent_result['usuario_id']

                # Dados do usuário
                cursor.execute("""
                    SELECT username, fotos_perfil FROM users WHERE id = %s
                """, (usuario_id,))
                usuario = cursor.fetchone()

                # Nova contagem de comentários
                cursor.execute("""
                    SELECT COUNT(*) as comentarios_count FROM comentarios WHERE post_id = %s
                """, (post_id,))
                comentarios_count = cursor.fetchone()['comentarios_count']

            conexao.commit()
            conexao.close()

            return jsonify(
                success=True, 
                comentario=str(replace_mentions_comentario(comentario)), # já com menções formatadas!!
                fotos_perfil=usuario['fotos_perfil'],
                username=usuario['username'], 
                data_comentario=formatar_data(datetime.now()),
                is_user_comment=True,
                usuario_id=usuario_id,
                comentarios_count=comentarios_count,
                comentario_id=comentario_id,
                parent_comment_id=parent_comment_id,
                parent_username=parent_username,
                parent_usuario_id=parent_usuario_id
            )

        return jsonify(success=False, error="Erro na conexão com o banco de dados"), 500

    except Exception as e:
        return jsonify(success=False, error=f"Erro ao conectar ao banco de dados: {str(e)}"), 500