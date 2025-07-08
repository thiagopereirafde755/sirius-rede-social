from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
from werkzeug.utils import secure_filename
from app.conexao import criar_conexao
from app.utils import replace_mentions, formatar_data, buscar_hashtags_mais_usadas
from datetime import datetime
from markupsafe import Markup
import re

inicio_bp = Blueprint('inicio', __name__)

# Registre o filtro Jinja2 usando a função importada
@inicio_bp.app_template_filter('replace_mentions')
def _replace_mentions(text):
    return replace_mentions(text)

@inicio_bp.route('/inicio')
def inicio():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()

        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Informações do usuário
                cursor.execute("SELECT nome, username, fotos_perfil, bio, foto_capa, tema FROM users WHERE id = %s", (usuario_id,))
                usuario = cursor.fetchone()

                # Contagem de posts
                cursor.execute("SELECT COUNT(*) as total_posts FROM posts WHERE users_id = %s", (usuario_id,))
                total_posts = cursor.fetchone()['total_posts']

                # Recuperar posts do usuário
                cursor.execute("SELECT *,  (SELECT COUNT(*) FROM comentarios WHERE comentarios.post_id = posts.id) AS comentarios_count" 
                " FROM posts WHERE users_id = %s ORDER BY data_postagem DESC", (usuario_id,))
                posts = cursor.fetchall()

                # HASHTAG DO MOMENTO
                hashtags_top = buscar_hashtags_mais_usadas(cursor)

                for post in posts:
                    post_id = post['id']
                    post['data_postagem'] = formatar_data(post['data_postagem'])

                    cursor.execute("""
                         SELECT comentarios_publicos FROM users WHERE id = %s
                     """, (post['users_id'],))
                    post['comentarios_publicos'] = cursor.fetchone()['comentarios_publicos']

                    cursor.execute("""
                        SELECT COUNT(*) AS visualizacoes
                        FROM visualizacoes
                        WHERE post_id = %s
                    """, (post_id,))
                    resultado = cursor.fetchone()
                    post['visualizacoes'] = resultado['visualizacoes'] if resultado else 0


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
                    cursor.execute("""
                        SELECT * FROM curtidas 
                        WHERE post_id = %s AND usuario_id = %s
                    """, (post_id, usuario_id))
                    post['curtido_pelo_usuario'] = cursor.fetchone() is not None

                    # Contar curtidas do post
                    cursor.execute("""SELECT COUNT(*) as curtidas FROM curtidas WHERE post_id = %s""", (post['id'],))
                    post['curtidas'] = cursor.fetchone()['curtidas']

                # Informações do perfil do usuário
                if usuario:
                    nome_completo = usuario['nome']
                    nome_usuario = usuario['username']
                    foto_perfil = usuario['fotos_perfil'] if usuario['fotos_perfil'] else url_for('static', filename='img/icone/user.png')
                    bio_user = usuario['bio']
                    foto_capa = usuario['foto_capa'] if usuario['foto_capa'] else url_for('static', filename='img/icone/redes-sociais-capa-1.jpg')
                    tema = usuario.get('tema', 'claro')
                else:
                    nome_completo = None
                    nome_usuario = None
                    foto_perfil = url_for('static', filename='img/icone/user.png')
                    bio_user = None
                    foto_capa = url_for('static', filename='img/icone/redes-sociais-capa-1.jpg')
                    tema = 'claro'

                # Contagem de seguidores e seguindo
                cursor.execute("""SELECT COUNT(*) FROM seguindo WHERE id_seguindo = %s""", (usuario_id,))
                seguidores_count = cursor.fetchone()['COUNT(*)']

                cursor.execute("""SELECT COUNT(*) FROM seguindo WHERE id_seguidor = %s""", (usuario_id,))
                seguindo_count = cursor.fetchone()['COUNT(*)']

                # Lista de seguidores
                cursor.execute("""
                    SELECT u.id, u.username, u.fotos_perfil
                    FROM users u
                    JOIN seguindo s ON u.id = s.id_seguidor
                    WHERE s.id_seguindo = %s
                """, (usuario_id,))
                seguidores_lista = cursor.fetchall()

                # Lista de seguindo
                cursor.execute("""
                    SELECT u.id, u.username, u.fotos_perfil
                    FROM users u
                    JOIN seguindo s ON u.id = s.id_seguindo
                    WHERE s.id_seguidor = %s
                """, (usuario_id,))
                seguindo_lista = cursor.fetchall()

            conexao.close()

            return render_template('pagina-inicial.html', nome=nome_completo, 
                                   username=nome_usuario, 
                                   foto_perfil=foto_perfil, 
                                   bio=bio_user, 
                                   foto_capa=foto_capa, 
                                   posts=posts, 
                                   usuario_id=usuario_id, 
                                   seguidores=seguidores_count, 
                                   seguindo=seguindo_count, 
                                   seguidores_lista=seguidores_lista, 
                                   seguindo_lista=seguindo_lista, 
                                   total_posts=total_posts, 
                                   nome_usuario=nome_usuario,  
                                   hashtags_top=hashtags_top,
                                   tema=tema,)

        return "Erro na conexão com o banco de dados."

    except Exception as e:
        return f"Erro ao conectar ao banco de dados. Detalhes: {str(e)}"
    
