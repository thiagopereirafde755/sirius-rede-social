from flask import Blueprint, request, session, jsonify
from app.utils import extrair_mencoes, formatar_data, replace_mentions_com_id, verificar_seguidores_mutuos
from app.conexao import criar_conexao
from datetime import datetime

comentar_bp = Blueprint('comentar', __name__)

# =============================================================
#  PARA COMENTAR EM POST
# =============================================================
@comentar_bp.route('/comentar/<int:post_id>', methods=['POST'])
def comentar(post_id):
    if 'usuario_id' not in session:
        return jsonify(success=False, error="Usuário não está logado"), 403

    usuario_id = session['usuario_id']
    comentario = request.form.get('comentario', '').strip()
    parent_comment_id = request.form.get('parent_comment_id', None)

    if not comentario:
        return jsonify(success=False, error="Comentário vazio"), 400

    try:
        conexao = criar_conexao()
        if not conexao:
            return jsonify(success=False, error="Erro na conexão com o banco de dados"), 500

        with conexao.cursor(dictionary=True) as cursor:

            # VERIFICA A CONF DO POST
            cursor.execute("""
                SELECT p.users_id, u.comentarios_publicos 
                FROM posts p
                JOIN users u ON p.users_id = u.id
                WHERE p.id = %s
            """, (post_id,))
            post_info = cursor.fetchone()
            if not post_info:
                return jsonify(success=False, error="Post não encontrado"), 404

            comentarios_publicos = post_info['comentarios_publicos']
            dono_post_id = post_info['users_id']

            # CONTROLE DE PERMISAO
            permitido = (
                comentarios_publicos == 'todos' or
                usuario_id == dono_post_id or
                (
                    comentarios_publicos == 'seguidores_mutuos' and 
                    verificar_seguidores_mutuos(usuario_id, dono_post_id)
                )
            )
            if not permitido:
                return jsonify(success=False, error="Você não tem permissão para comentar neste post."), 403

            # INSERE OS COMENTARIOS
            cursor.execute("""
                INSERT INTO comentarios (post_id, usuario_id, comentario, parent_comment_id) 
                VALUES (%s, %s, %s, %s)
            """, (post_id, usuario_id, comentario, parent_comment_id))
            comentario_id = cursor.lastrowid

            # MENÇÕES
            mencoes = extrair_mencoes(comentario)
            mapa_mencoes = {}
            if mencoes:
                formato = ','.join(['%s'] * len(mencoes))
                cursor.execute(f"SELECT id, username FROM users WHERE username IN ({formato})", tuple(mencoes))
                resultados = cursor.fetchall()
                for row in resultados:
                    mapa_mencoes[row['username'].lower()] = row['id']

            for username in mencoes:
                mencionado_id = mapa_mencoes.get(username.lower())
                if mencionado_id and mencionado_id != usuario_id:
                    cursor.execute("""
                        INSERT INTO comentario_mencoes (comentario_id, user_mencionado_id)
                        VALUES (%s, %s)
                    """, (comentario_id, mencionado_id))
                    cursor.execute("""
                        INSERT INTO notificacoes (usuario_id, tipo, origem_usuario_id, post_id, comentario_id, lida)
                        VALUES (%s, 'mencao', %s, %s, %s, 0)
                    """, (mencionado_id, usuario_id, post_id, comentario_id))

            # NOTIFICACAO
            if usuario_id != dono_post_id and not parent_comment_id:
                cursor.execute("""
                    INSERT INTO notificacoes (usuario_id, tipo, origem_usuario_id, post_id, comentario_id)
                    VALUES (%s, 'comentario', %s, %s, %s)
                """, (dono_post_id, usuario_id, post_id, comentario_id))

            # NOTIFICACAO PARA O AUTOR DA RESPOSTA
            parent_username = None
            parent_usuario_id = None
            if parent_comment_id:
                cursor.execute("SELECT usuario_id FROM comentarios WHERE id = %s", (parent_comment_id,))
                dono_resposta = cursor.fetchone()
                if dono_resposta and dono_resposta['usuario_id'] != usuario_id:
                    cursor.execute("""
                        INSERT INTO notificacoes (usuario_id, tipo, origem_usuario_id, post_id, comentario_id)
                        VALUES (%s, 'resposta', %s, %s, %s)
                    """, (dono_resposta['usuario_id'], usuario_id, post_id, comentario_id))
                cursor.execute("""
                    SELECT u.username, u.id 
                    FROM comentarios c
                    JOIN users u ON c.usuario_id = u.id
                    WHERE c.id = %s
                """, (parent_comment_id,))
                parent_info = cursor.fetchone()
                if parent_info:
                    parent_username = parent_info['username']
                    parent_usuario_id = parent_info['id']

            # DADOS DE QUEM COMENTOU
            cursor.execute("SELECT username, fotos_perfil FROM users WHERE id = %s", (usuario_id,))
            usuario = cursor.fetchone()

            # ATUALIZA A CONTAGEM
            cursor.execute("SELECT COUNT(*) as comentarios_count FROM comentarios WHERE post_id = %s", (post_id,))
            comentarios_count = cursor.fetchone()['comentarios_count']

        conexao.commit()
        conexao.close()

        comentario_formatado = replace_mentions_com_id(comentario, mapa_mencoes)

        return jsonify(
            success=True,
            comentario=comentario_formatado,
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

    except Exception as e:
        return jsonify(success=False, error=f"Erro ao comentar: {str(e)}"), 500
