import os
from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from werkzeug.utils import secure_filename
from app.conexao import criar_conexao
from app.utils import replace_mentions, formatar_data, gerar_filtros_busca
from flask import jsonify
from datetime import datetime

posteseguindo_bp = Blueprint('post-seguindo', __name__)

posteseguindo_bp.app_template_filter('replace_mentions')
def _replace_mentions(text):
    return replace_mentions(text)

@posteseguindo_bp.route('/post-seguindo')
def home():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))  # Redireciona se não estiver logado

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()

        if conexao:
            with conexao.cursor(dictionary=True) as cursor:

                 # Informações do usuário
                cursor.execute("SELECT fotos_perfil, username, tema FROM users WHERE id = %s", (usuario_id,))
                usuario = cursor.fetchone()

                # Informações do perfil do usuário
                if usuario:
                    nome_usuario = usuario['username']
                    tema = usuario.get('tema', 'claro')  # agora funciona
                    foto_perfil = usuario['fotos_perfil'] if usuario['fotos_perfil'] else url_for('static', filename='img/icone/user.png')
                else:
                    foto_perfil = url_for('static', filename='img/icone/user.png')
                    tema = 'claro'

              # Pegando os posts das pessoas que o usuário segue, incluindo a contagem de comentários
                cursor.execute("""
    SELECT 
        posts.*, 
        users.username, 
        users.fotos_perfil, 
        posts.users_id, 
        users.curtidas_publicas,
        (
            SELECT COUNT(*) 
            FROM comentarios 
            WHERE comentarios.post_id = posts.id
        ) AS comentarios_count
    FROM posts
    JOIN users ON posts.users_id = users.id
    JOIN seguindo ON seguindo.id_seguindo = users.id
    WHERE 
        seguindo.id_seguidor = %s
        -- Verifica se não foi bloqueado pelo seguido
        AND NOT EXISTS (
            SELECT 1 
            FROM bloqueados 
            WHERE usuario_id = posts.users_id AND bloqueado_id = %s
        )
    ORDER BY
        -- 1º: posts curtidos por mim
        (
            SELECT COUNT(*) 
            FROM curtidas 
            WHERE curtidas.post_id = posts.id AND curtidas.usuario_id = %s
        ) DESC,
        -- 2º: posts mais curtidos em geral
        (
            SELECT COUNT(*) 
            FROM curtidas 
            WHERE curtidas.post_id = posts.id
        ) DESC,
        -- 3º: posts mais recentes
        posts.data_postagem DESC
""", (usuario_id, usuario_id, usuario_id))

                posts = cursor.fetchall()

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

                for post in posts:
                    post_id = post['id']
                    post['data_postagem'] = formatar_data(post['data_postagem'])

                    # Pegando as curtidas
                    cursor.execute("""
                        SELECT COUNT(*) as curtidas
                        FROM curtidas 
                        WHERE post_id = %s
                    """, (post['id'],))
                    post['curtidas'] = cursor.fetchone()['curtidas']

                    # Verificar se o usuário já segue o autor do post
                    cursor.execute("""
                        SELECT * FROM seguindo 
                        WHERE id_seguidor = %s AND id_seguindo = %s
                    """, (usuario_id, post['users_id']))
                    post['seguindo'] = cursor.fetchone() is not None

                    # Verificar se o usuário já curtiu o post
                    cursor.execute("""
                        SELECT * FROM curtidas 
                        WHERE post_id = %s AND usuario_id = %s
                    """, (post['id'], usuario_id))
                    post['curtido_pelo_usuario'] = cursor.fetchone() is not None

                    # Verificando se o usuário logado já curtiu o post
                    cursor.execute("""
                        SELECT 1 
                        FROM curtidas 
                        WHERE post_id = %s AND usuario_id = %s
                    """, (post['id'], usuario_id))
                    post['usuario_curtiu'] = cursor.fetchone() is not None

                    cursor.execute("""
                         SELECT comentarios_publicos FROM users WHERE id = %s
                     """, (post['users_id'],))
                    post['comentarios_publicos'] = cursor.fetchone()['comentarios_publicos']

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

                
            conexao.close()

            return render_template('posts-seguindo.html', posts=posts, usuario_id=usuario_id, foto_perfil=foto_perfil, nome_usuario=nome_usuario, hashtags_top=hashtags_top, tema=tema)
        
        return "Erro na conexão com o banco de dados."

    except Exception as e:
        return f"Erro ao conectar ao banco de dados: {str(e)}"
    
@posteseguindo_bp.route('/pesquisar-seguindo')
def pesquisar_seguindo():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))  # Redireciona se não estiver logado

    usuario_id = session['usuario_id']
    query = request.args.get('query', '').strip()
    filtro = request.args.get('filtro', 'mais_recente')  # Novo: pega filtro do GET
    tipo_conteudo = request.args.get('tipo_conteudo', 'geral')

    try:
        conexao = criar_conexao()

        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Informações do usuário
                cursor.execute("SELECT fotos_perfil, username, tema FROM users WHERE id = %s", (usuario_id,))
                usuario = cursor.fetchone()

                if usuario:
                    nome_usuario = usuario['username']
                    tema = usuario.get('tema', 'claro')  # agora funciona
                    foto_perfil = usuario['fotos_perfil'] if usuario['fotos_perfil'] else url_for('static', filename='img/icone/user.png')
                else:
                    foto_perfil = url_for('static', filename='img/icone/user.png')
                    tema = 'claro'

                # Define o ORDER BY conforme filtro
                order_by, filtro_tipo = gerar_filtros_busca(filtro, tipo_conteudo)


                # Pegando os posts das pessoas que o usuário segue, filtrando por conteúdo ou nome de usuário
                cursor.execute(f"""
                    SELECT posts.*, users.username, users.fotos_perfil, posts.users_id, users.curtidas_publicas,
                    (SELECT COUNT(*) FROM comentarios WHERE comentarios.post_id = posts.id) AS comentarios_count,
                    (SELECT COUNT(*) FROM curtidas WHERE curtidas.post_id = posts.id) AS curtidas
                    FROM posts
                    JOIN users ON posts.users_id = users.id
                    JOIN seguindo ON seguindo.id_seguindo = users.id
                    WHERE seguindo.id_seguidor = %s
                    AND (posts.conteudo LIKE %s OR users.username LIKE %s)
                    {filtro_tipo} {order_by}
                """, (usuario_id, f"%{query}%", f"%{query}%"))
                posts = cursor.fetchall()

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

                for post in posts:
                    post_id = post['id']
                    post['data_postagem'] = formatar_data(post['data_postagem'])
                    # As curtidas já vieram da query

                    # Verificar se o usuário já curtiu o post
                    cursor.execute("""
                        SELECT * FROM curtidas 
                        WHERE post_id = %s AND usuario_id = %s
                    """, (post['id'], usuario_id))
                    post['curtido_pelo_usuario'] = cursor.fetchone() is not None

                    cursor.execute("""
                        SELECT comentarios_publicos FROM users WHERE id = %s
                    """, (post['users_id'],))
                    post['comentarios_publicos'] = cursor.fetchone()['comentarios_publicos']

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

            conexao.close()
            # Passe o filtro para o template também!
            return render_template(
                'posts-seguindo.html',
                posts=posts,
                usuario_id=usuario_id,
                foto_perfil=foto_perfil,
                query=query,
                nome_usuario=nome_usuario,
                hashtags_top=hashtags_top,
                filtro=filtro,
                tipo_conteudo=tipo_conteudo,
                tema=tema
            )
        
        return "Erro na conexão com o banco de dados."

    except Exception as e:
        return f"Erro ao conectar ao banco de dados: {str(e)}"