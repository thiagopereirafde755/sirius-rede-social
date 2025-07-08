import os
from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
from werkzeug.utils import secure_filename
from app.utils import replace_mentions, formatar_data, replace_hashtags
from app.conexao import criar_conexao
from datetime import datetime

info_bp = Blueprint('info_user', __name__)

# Registre o filtro Jinja2 usando a função importada
@info_bp.app_template_filter('replace_mentions')
def _replace_mentions(text):
    return replace_mentions(text)

@info_bp.app_template_filter('replace_hashtags')
def _replace_hashtags(text):
    return replace_hashtags(text)

@info_bp.route('/info-user/<int:id_usuario>')
def info_user(id_usuario):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    if id_usuario == usuario_id:
        return redirect(url_for('inicio.inicio'))

    try:
        conexao = criar_conexao()
        if not conexao:
            return redirect(url_for('home.home'))

        with conexao.cursor(dictionary=True) as cursor:
            # Verifica se o usuário visitado existe
            cursor.execute("SELECT id FROM users WHERE id = %s", (id_usuario,))
            if not cursor.fetchone():
                conexao.close()
                return redirect(url_for('home.home'))

            # Busca dados do usuário logado (tema, foto, username)
            cursor.execute("SELECT fotos_perfil, username, tema FROM users WHERE id = %s", (usuario_id,))
            usuario_logado = cursor.fetchone()

            nome_usuario_logado = usuario_logado['username'] if usuario_logado else "Usuário"
            foto_perfil_logado = usuario_logado['fotos_perfil'] if usuario_logado and usuario_logado['fotos_perfil'] else url_for('static', filename='img/icone/user.png')
            tema = usuario_logado['tema'] if usuario_logado and usuario_logado.get('tema') else 'claro'

            # Verifica se você bloqueou esse usuário
            cursor.execute("SELECT * FROM bloqueados WHERE usuario_id = %s AND bloqueado_id = %s", (usuario_id, id_usuario))
            voce_bloqueou = cursor.fetchone()

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

            # Verifica se o usuário visitado bloqueou você
            cursor.execute("SELECT * FROM bloqueados WHERE usuario_id = %s AND bloqueado_id = %s", (id_usuario, usuario_id))
            if cursor.fetchone():
                cursor.execute("SELECT username FROM users WHERE id = %s", (id_usuario,))
                bloqueador = cursor.fetchone()
                conexao.close()
                return render_template('informacao-user.html',
                    usuario_bloqueou=True,
                    username_bloqueador=bloqueador['username'],
                    foto_perfil_logado=foto_perfil_logado,
                    nome_usuario_logado=nome_usuario_logado,
                    usuario_id=usuario_id,
                    foto_perfil=url_for('static', filename='img/icone/user.png'),
                    username="",
                    nome="",
                    bio="",
                    foto_capa=url_for('static', filename='img/icone/redes-sociais-capa-1.jpg'),
                    tema=tema,
                    hashtags_top=hashtags_top,
                )

            # Informações do perfil visitado
            cursor.execute("SELECT nome, username, fotos_perfil, bio, foto_capa, perfil_publico, visibilidade_seguidores  FROM users WHERE id = %s", (id_usuario,))
            usuario = cursor.fetchone()
            if not usuario:
                return "Usuário não encontrado."

            # Verifica se o usuário logado segue o perfil
            cursor.execute("SELECT * FROM seguindo WHERE id_seguidor = %s AND id_seguindo = %s", (usuario_id, id_usuario))
            usuario_segue = cursor.fetchone()

            visibilidade_seguidores = usuario['visibilidade_seguidores']
            perfil_publico = usuario['perfil_publico']
            mostrar_postagens = perfil_publico or usuario_segue

            # Contagem de posts
            cursor.execute("SELECT COUNT(*) as total_posts FROM posts WHERE users_id = %s", (id_usuario,))
            total_posts = cursor.fetchone()['total_posts']

            # Pegando as postagens do usuário específico se o perfil for público ou se o usuário logado for seguidor
            posts = []
            if mostrar_postagens:
                cursor.execute("""
                    SELECT posts.*, 
                           (SELECT COUNT(*) FROM comentarios WHERE comentarios.post_id = posts.id) AS comentarios_count
                    FROM posts 
                    WHERE users_id = %s 
                    ORDER BY data_postagem DESC
                """, (id_usuario,))
                posts = cursor.fetchall()
                for post in posts:
                    post_id = post['id']
                    post['data_postagem'] = formatar_data(post['data_postagem'])
                    cursor.execute("SELECT comentarios_publicos, curtidas_publicas FROM users WHERE id = %s", (post['users_id'],))
                    usuario_info = cursor.fetchone()
                    post['comentarios_publicos'] = usuario_info['comentarios_publicos']
                    post['curtidas_publicas'] = usuario_info['curtidas_publicas']

                    # Buscando comentários
                    cursor.execute("""
                        SELECT 
                            c.*, 
                            u.username, 
                            u.id AS usuario_id, 
                            u.fotos_perfil,
                            parent.id AS parent_comment_id,
                            parent.usuario_id AS parent_usuario_id,
                            parent_user.username AS parent_username,
                            (SELECT COUNT(*) FROM comentarios WHERE parent_comment_id = c.id) AS respostas_count
                        FROM comentarios c
                        JOIN users u ON c.usuario_id = u.id
                        LEFT JOIN comentarios parent ON c.parent_comment_id = parent.id
                        LEFT JOIN users parent_user ON parent.usuario_id = parent_user.id
                        WHERE c.post_id = %s
                        ORDER BY 
                            CASE WHEN c.parent_comment_id IS NULL THEN c.id ELSE c.parent_comment_id END,
                            c.id
                    """, (post['id'],))
                    comentarios = cursor.fetchall()
                    for comentario in comentarios:
                        comentario['data_comentario'] = formatar_data(comentario['data_comentario'])
                        if not comentario['fotos_perfil']:
                            comentario['fotos_perfil'] = url_for('static', filename='img/icone/user.png')
                    post['comentarios'] = comentarios

                    # Verificar se o usuário já curtiu o post
                    cursor.execute("SELECT * FROM curtidas WHERE post_id = %s AND usuario_id = %s", (post_id, usuario_id))
                    post['curtido_pelo_usuario'] = cursor.fetchone() is not None

                    # Contar curtidas do post
                    cursor.execute("SELECT COUNT(*) as curtidas FROM curtidas WHERE post_id = %s", (post['id'],))
                    post['curtidas'] = cursor.fetchone()['curtidas']

            # Contando os seguidores
            cursor.execute("SELECT COUNT(*) as seguidores_count FROM seguindo WHERE id_seguindo = %s", (id_usuario,))
            seguidores_count = cursor.fetchone()['seguidores_count']

            # Contando os seguidos
            cursor.execute("SELECT COUNT(*) as seguindo_count FROM seguindo WHERE id_seguidor = %s", (id_usuario,))
            seguindo_count = cursor.fetchone()['seguindo_count']

            # Pegando os seguidores do usuário
            cursor.execute("SELECT u.id, u.username, u.fotos_perfil FROM users u JOIN seguindo s ON u.id = s.id_seguidor WHERE s.id_seguindo = %s", (id_usuario,))
            seguidores_lista = cursor.fetchall()
        
        # Pegando os seguidos do usuário (correto)
            cursor.execute(
                "SELECT u.id, u.username, u.fotos_perfil FROM users u JOIN seguindo s ON u.id = s.id_seguindo WHERE s.id_seguidor = %s", 
                (id_usuario,)
            )
            seguindo_lista = cursor.fetchall()

            # Verifica se há pedido de seguir pendente
            cursor.execute("SELECT * FROM pedidos_seguir WHERE id_solicitante = %s AND id_destino = %s", (usuario_id, id_usuario))
            pedido_pendente = cursor.fetchone() is not None

            # Verifica se o usuário que estamos vendo segue o usuário logado
            cursor.execute("SELECT * FROM seguindo WHERE id_seguidor = %s AND id_seguindo = %s", (id_usuario, usuario_id))
            usuario_te_segue = cursor.fetchone()


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

        nome_completo = usuario['nome']
        nome_usuario = usuario['username']
        foto_perfil = usuario['fotos_perfil'] if usuario['fotos_perfil'] else url_for('static', filename='img/icone/user.png')
        bio_user = usuario['bio']
        foto_capa = usuario['foto_capa'] if usuario['foto_capa'] else url_for('static', filename='img/icone/redes-sociais-capa-1.jpg')

        return render_template('informacao-user.html', 
               nome=nome_completo, 
               username=nome_usuario, 
               foto_perfil=foto_perfil, 
               bio=bio_user, 
               foto_capa=foto_capa, 
               posts=posts, 
               usuario_segue=usuario_segue,
               id_usuario=id_usuario, 
               usuario_id=usuario_id,
               seguidores=seguidores_count,  
               seguindo=seguindo_count, 
               seguidores_lista=seguidores_lista,  
               seguindo_lista=seguindo_lista,
               foto_userlog=foto_perfil_logado,
               total_posts=total_posts,
               pedido_pendente=pedido_pendente,
               perfil_publico=perfil_publico,
               mostrar_postagens=mostrar_postagens,
               nome_usuario_logado=nome_usuario_logado,
               foto_perfil_logado=foto_perfil_logado,
               usuario_te_segue=usuario_te_segue,
               visibilidade_seguidores=visibilidade_seguidores,
               voce_bloqueou=voce_bloqueou,
               tema=tema,
               hashtags_top=hashtags_top,
               username_bloqueado=usuario['username'] if usuario else ""
        )

    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {str(e)}")
        return redirect(url_for('home.home'))

@info_bp.route('/obter_id_usuario')
def obter_id_usuario():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username não fornecido'}), 400
    
    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                usuario = cursor.fetchone()
                
                if usuario:
                    return jsonify({'id': usuario['id']})
                else:
                    return jsonify({'error': 'Usuário não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conexao' in locals() and conexao:
            conexao.close()
    
    return jsonify({'error': 'Erro ao buscar usuário'}), 500

