from flask import Blueprint, render_template, redirect, url_for, session
from app.conexao import criar_conexao
from app.utils import replace_mentions, buscar_hashtags_mais_usadas, obter_seguidores_e_seguindo, replace_hashtags, processar_posts, contar_seguidores_e_seguindo, contar_total_posts

inicio_bp = Blueprint('inicio', __name__)

# =============================================================
#  FUNÇÕES
# =============================================================
@inicio_bp.app_template_filter('replace_mentions')
def _replace_mentions(text):
    return replace_mentions(text)

@inicio_bp.app_template_filter('replace_hashtags')
def _replace_hashtags(text):
    return replace_hashtags(text)
# =============================================================
#  PAGINA INICIAL DO USER SEM ML
# =============================================================
@inicio_bp.route('/inicio')
def inicio():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()

        if conexao:
            with conexao.cursor(dictionary=True) as cursor:

                # INFORMAÇÃO DO USUARIO
                cursor.execute("""
                    SELECT nome, username, email,
                    DATE_FORMAT(data_cadastro, '%d/%m/%Y %H:%i') AS data_cadastro,
                    DATE_FORMAT(data_nascimento, '%d/%m/%Y') AS data_nascimento,
                    fotos_perfil, bio, foto_capa, tema 
                    FROM users WHERE id = %s
                """, (usuario_id,))
                usuario = cursor.fetchone()

                # CONTAR TOTAL POST
                total_posts = contar_total_posts(cursor, usuario_id)

                # PEGAR POST DO USER
                cursor.execute("""
                    SELECT *,
                    (SELECT COUNT(*) FROM comentarios WHERE comentarios.post_id = posts.id) AS comentarios_count
                    FROM posts WHERE users_id = %s ORDER BY data_postagem DESC
                """, (usuario_id,))
                posts = cursor.fetchall()

                # HASHTAG DO MOMENTO
                hashtags_top = buscar_hashtags_mais_usadas(cursor)

                # FOR DO POST
                posts = processar_posts(posts, usuario_id, cursor)

                # Dados do perfil do usuário
                if usuario:
                    nome_completo = usuario['nome']
                    nome_usuario = usuario['username']
                    foto_perfil = usuario['fotos_perfil'] if usuario['fotos_perfil'] else url_for('static', filename='img/icone/user.png')
                    bio_user = usuario['bio'] or ''
                    foto_capa = usuario['foto_capa'] if usuario['foto_capa'] else url_for('static', filename='img/icone/redes-sociais-capa-1.jpg')
                    tema = usuario.get('tema', 'claro')
                    email_user = usuario['email']
                    data_cadastro_user = usuario['data_cadastro']
                    data_nasc_user = usuario['data_nascimento'] or 'Não informado'
                else:
                    nome_completo = None
                    nome_usuario = None
                    foto_perfil = url_for('static', filename='img/icone/user.png')
                    bio_user = ''
                    foto_capa = url_for('static', filename='img/icone/redes-sociais-capa-1.jpg')
                    tema = 'claro'
                    email_user = None
                    data_cadastro_user = None
                    data_nasc_user = None

                # CONTAGEM DE SEGUIDORES E SEGUINDO
                seguidores_count, seguindo_count = contar_seguidores_e_seguindo(cursor, usuario_id)

                # LISTA DE SEGUIDORES E SEGUINDO
                listas = obter_seguidores_e_seguindo(cursor, usuario_id)
                seguidores_lista = listas['seguidores_lista']
                seguindo_lista = listas['seguindo_lista']

            conexao.close()

            return render_template('pagina-inicial.html',
                                   nome=nome_completo,
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
                                   tema=tema,
                                   email=email_user,
                                   data_cadastro=data_cadastro_user,
                                   data_nascimento=data_nasc_user)

        return "Erro na conexão com o banco de dados."

    except Exception as e:
        return f"Erro ao conectar ao banco de dados. Detalhes: {str(e)}"


