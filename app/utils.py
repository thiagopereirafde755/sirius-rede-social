import re
from markupsafe import Markup
from datetime import datetime
from urllib.parse import quote 
from flask import Blueprint, render_template, redirect, url_for, session, request, flash, Request
from app.conexao import criar_conexao
import pickle
from datetime import datetime
import pandas as pb
# =============================================================
#  REDERIZAR O sweetalert2 NO PYTHON
# =============================================================
def render_swal_alert(swal_script):
    """Função auxiliar para renderizar o SweetAlert com HTML básico"""
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Redirecionando...</title>
        <link rel="icon" type="image/png" sizes="16x16" href="../static/img/logo/logo_sirius.png">
        <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
        <link rel="stylesheet" href="../static/css/style1.css" />
    </head>
    <body>
        {swal_script}
    </body>
    </html>
    '''
# =============================================================
#  INFORMAÇOES DO USUARIO LOGADO
# =============================================================
def buscar_info_usuario_logado_1(cursor, usuario_id):
    cursor.execute("SELECT fotos_perfil, username, tema FROM users WHERE id = %s", (usuario_id,))
    usuario = cursor.fetchone()

    if usuario:
        foto_perfil = usuario['fotos_perfil'] if usuario['fotos_perfil'] else url_for('static', filename='img/icone/user.png')
        nome_usuario = usuario['username']
        tema = usuario.get('tema', 'claro')
    else:
        foto_perfil = url_for('static', filename='img/icone/user.png')
        nome_usuario = ""
        tema = 'claro'

    return foto_perfil, nome_usuario, tema

# =============================================================
#  HASHTAGS
# =============================================================
def extrair_hashtags(texto):
    return set(re.findall(r'#\w+', texto or ""))

def replace_hashtags(text):
    hashtag_pattern = r'(?P<hashtag>#\w+)'
    def repl(match):
        hashtag = match.group('hashtag')
        url = f"/pesquisar?query={quote(hashtag)}"  
        return f'<a href="{url}" class="hashtag-link">{hashtag}</a>'
    return Markup(re.sub(hashtag_pattern, repl, text))

def buscar_hashtags_mais_usadas(cursor):
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
    return cursor.fetchall()
# =============================================================
#  MENCIONAR USUARIO EM POST
# =============================================================
def extrair_mencoes(texto):
    """Extrai nomes de usuário mencionados com @ em um texto."""
    return set(re.findall(r'@([A-Za-z0-9_.-]+)', texto or ""))

def replace_mentions_comentario(text):
    """Transforma menções @username em links HTML seguros."""
    mention_pattern = re.compile(r'(?<!\w)@([A-Za-z0-9_.-]+)')
    def replace_match(match):
        username = match.group(1)
        return f'<a href="/obter_id_usuario?username={username}" class="mention-link" data-username="{username}">@{username}</a>'
    safe_text = Markup.escape(text)
    return Markup(mention_pattern.sub(replace_match, safe_text))

def replace_mentions(text):
    if not text:
        return ""
    mention_pattern = re.compile(r'(?<!\w)@([A-Za-z0-9_.-]+)')
    def replace_match(match):
        username = match.group(1)
        return f'<a href="/obter_id_usuario?username={username}" class="mention-link" data-username="{username}">@{username}</a>'
    safe_text = Markup.escape(text)
    return Markup(mention_pattern.sub(replace_match, safe_text))
# =============================================================
#  FORMATAR A DATA DO POST 
# =============================================================
def formatar_data(data_postagem):
    now = datetime.now()
    diff = now - data_postagem
    diff_seconds = int(diff.total_seconds())
    if diff_seconds < 60:
        return f"há {diff_seconds} segundo(s)"
    elif diff_seconds < 3600:
        minutes = diff_seconds // 60
        return f"há {minutes} minuto(s)"
    elif diff_seconds < 86400:
        hours = diff_seconds // 3600
        return f"há {hours} hora(s)"
    elif diff_seconds < 2592000:
        days = diff_seconds // 86400
        return f"há {days} dia(s)"
    elif diff_seconds < 31536000:
        months = diff_seconds // 2592000
        return f"há {months} mês(es)"
    else:
        years = diff_seconds // 31536000
        return f"há {years} ano(s)"
# =============================================================
#  BUSCAR COMENTARIOS DO POST
# =============================================================
def buscar_comentarios_post(cursor, post_id):
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
    """, (post_id,))
    
    comentarios = cursor.fetchall()

    for comentario in comentarios:
        comentario['data_comentario'] = formatar_data(comentario['data_comentario'])
        if not comentario['fotos_perfil']:
            comentario['fotos_perfil'] = url_for('static', filename='img/icone/user.png')
        if 'parent_usuario_id' not in comentario:
            comentario['parent_usuario_id'] = None
            comentario['parent_username'] = None

    return comentarios
# =============================================================
#  CONSULTA PARA PEGAR AS CURTIDAS
# =============================================================
def buscar_total_curtidas(cursor, post_id):
    cursor.execute("""
        SELECT COUNT(*) as curtidas
        FROM curtidas 
        WHERE post_id = %s
    """, (post_id,))
    resultado = cursor.fetchone()
    return resultado['curtidas'] if resultado else 0
# =============================================================
#  CONTA QUANTAS VISUALIZAÇOES TEVE O POST
# =============================================================
def buscar_total_visualizacoes(cursor, post_id):
    cursor.execute("""
        SELECT COUNT(*) AS visualizacoes
        FROM visualizacoes
        WHERE post_id = %s
    """, (post_id,))
    resultado = cursor.fetchone()
    return resultado['visualizacoes'] if resultado else 0
# =============================================================
#  VERIFICA SE O USUARIO CURTIU O POST
# =============================================================
def verificar_curtida(cursor, post_id, usuario_id):
    cursor.execute("""
        SELECT 1 FROM curtidas 
        WHERE post_id = %s AND usuario_id = %s
        LIMIT 1
    """, (post_id, usuario_id))
    return cursor.fetchone() is not None
# =============================================================
#  BUSCAR COMENTARIOS PUBLICO
# =============================================================
def buscar_comentarios_publicos(cursor, user_id):
    cursor.execute("""
        SELECT comentarios_publicos FROM users WHERE id = %s
    """, (user_id,))
    resultado = cursor.fetchone()
    return resultado['comentarios_publicos'] if resultado else 1  
# =============================================================
#  SE O USER SEGUI O DONO DO POST 
# =============================================================
def verificar_seguindo_postindividual(cursor, id_seguidor, id_seguindo):
    cursor.execute("""
        SELECT 1 FROM seguindo 
        WHERE id_seguidor = %s AND id_seguindo = %s
        LIMIT 1
    """, (id_seguidor, id_seguindo))
    return cursor.fetchone() is not None
# =============================================================
#  BUSCAR POST
# =============================================================
def processar_posts(posts, usuario_id, cursor):
    # BUSCAR TOP HASHTGS
    cursor.execute("""
        SELECT h.id
        FROM hashtags h
        JOIN post_hashtags ph ON h.id = ph.hashtag_id
        JOIN posts p ON ph.post_id = p.id
        WHERE p.data_postagem >= NOW() - INTERVAL 10 HOUR
        GROUP BY h.id
        ORDER BY COUNT(*) DESC
        LIMIT 3
    """)
    top_hashtag_ids = [row['id'] for row in cursor.fetchall()]

    for post in posts:
        post_id = post['id']
        post['data_postagem'] = formatar_data(post['data_postagem']) 

        # CALCULA O TEMPO DA POSTAGEM
        cursor.execute("SELECT data_postagem FROM posts WHERE id = %s", (post_id,))
        data_real = cursor.fetchone()['data_postagem']
        post['tempo_post'] = int((datetime.now() - data_real).total_seconds() / 3600)

        # VERIFICA SE O POST TEM HASTAGS POPULAR
        cursor.execute("SELECT hashtag_id FROM post_hashtags WHERE post_id = %s", (post_id,))
        hashtags_post = [row['hashtag_id'] for row in cursor.fetchall()]
        post['top_hashtag'] = any(h in top_hashtag_ids for h in hashtags_post)

        # CONTA A CURTIDA
        post['curtidas'] = buscar_total_curtidas(cursor, post['id'])

        # CONTA AS VISUALIZAÇÕES
        post['visualizacoes'] = buscar_total_visualizacoes(cursor, post_id)

        # SE O USER CURTIU
        post['curtido_pelo_usuario'] = verificar_curtida(cursor, post['id'], usuario_id)

        # SE OS COMENTARIOS SAO PUBLICOS
        post['comentarios_publicos'] = buscar_comentarios_publicos(cursor, post['users_id'])

        # SE O USER SEGUI O DONO DO POST
        cursor.execute("SELECT 1 FROM seguindo WHERE id_seguidor = %s AND id_seguindo = %s", (usuario_id, post['users_id']))
        post['seguindo'] = cursor.fetchone() is not None

        # COMENTARIOS
        post['comentarios'] = buscar_comentarios_post(cursor, post_id)

    return posts
# =============================================================
#  FILTRO PARA PESQUISA
# =============================================================
def gerar_filtros_busca(filtro: str, tipo_conteudo: str) -> tuple[str, str]:
    if filtro == 'mais_curtido':
        order_by = "ORDER BY curtidas DESC"
    elif filtro == 'mais_velho':
        order_by = "ORDER BY posts.data_postagem ASC"
    elif filtro == 'relevancia':
        order_by = ""  # sem ordenação, ML decide depois
    else:  # padrão: mais_recente
        order_by = "ORDER BY posts.data_postagem DESC"

    if tipo_conteudo == 'foto':
        filtro_tipo = (
            "AND posts.imagem IS NOT NULL AND posts.imagem != '' "
            "AND (posts.video IS NULL OR posts.video = '')"
        )
    elif tipo_conteudo == 'video':
        filtro_tipo = (
            "AND posts.video IS NOT NULL AND posts.video != '' "
            "AND (posts.imagem IS NULL OR posts.imagem = '')"
        )
    else:
        filtro_tipo = ""

    return order_by, filtro_tipo
# =============================================================
#  PARA O MODELO ML
# =============================================================
def extrair_features_post(post, usuario_id):
    return {
        'curtiu': int(post.get('curtido_pelo_usuario', False)),
        'comentou': int(any(c['usuario_id'] == usuario_id for c in post.get('comentarios', []))),
        'segue_autor': int(post.get('seguindo', False)),
        'perfil_publico': int(post.get('perfil_publico', 1)),
        'curtidas_post': int(post.get('curtidas', 0)),
        'comentarios_post': int(post.get('comentarios_count', 0)),
        'tempo_post': int(post.get('tempo_post', 0)),
        'top_hashtag': int(post.get('top_hashtag', 0)),
        'ja_visto': int(post.get('ja_visto', 0))  # NOVA FEATURE
    }

def aplicar_ranking_personalizado(posts, usuario_id, modelo_ml):
    import pandas as pd

    # Extrai os dados de features
    dados_features = [extrair_features_post(post, usuario_id) for post in posts]
    df = pd.DataFrame(dados_features)

    if df.empty:
        return posts 

    scores = modelo_ml.predict_proba(df)[:, 1]

    # PESOS
    peso_score_ml = 2.5
    peso_curtidas = 2.0
    peso_comentarios = 2.5
    peso_seguindo = 1.8
    peso_frescor = 0.15
    peso_ja_visto = -3.0

    for i, post in enumerate(posts):
        score_ml = scores[i]
        post['score_ml'] = round(score_ml, 4)

        curtidas = post.get('curtidas', 0)
        comentarios = post.get('comentarios_count', 0)
        seguindo = int(post.get('seguindo', False))
        tempo_post = post.get('tempo_post', 0)
        ja_visto = int(post.get('ja_visto', 0))
        
        # PESO BONUS
        frescor = max(0, (24 - tempo_post)) * peso_frescor

        post['score_total'] = round(
            score_ml * peso_score_ml +
            curtidas * peso_curtidas +
            comentarios * peso_comentarios +
            seguindo * peso_seguindo +
            frescor +
            ja_visto * peso_ja_visto, 4
        )

    # ORDENA PELO SCORE TOTAL
    posts.sort(key=lambda x: x['score_total'], reverse=True)
    return posts
