import re
from markupsafe import Markup
from datetime import datetime
from urllib.parse import quote 
from flask import  url_for, render_template_string
from datetime import datetime, timedelta
from app.conexao import criar_conexao

# =============================================================
#  LISTA CONTATOS 
# =============================================================
def buscar_contatos(usuario_id):
    conexao = criar_conexao()
    contatos = []

    try:
        with conexao.cursor(dictionary=True) as cursor:

            # BUSCA QUEM EU SIGO
            cursor.execute("""
                SELECT u.id, u.username, u.fotos_perfil,
                    COALESCE(MAX(m.data_envio), '1900-01-01') as ultima_mensagem
                FROM users u
                JOIN seguindo s1 ON u.id = s1.id_seguindo
                JOIN seguindo s2 ON u.id = s2.id_seguidor AND s2.id_seguindo = s1.id_seguidor
                LEFT JOIN mensagens m ON
                    ((m.id_remetente = u.id AND m.id_destinatario = %s) OR
                    (m.id_destinatario = u.id AND m.id_remetente = %s))
                WHERE s1.id_seguidor = %s
                GROUP BY u.id, u.username, u.fotos_perfil
                ORDER BY ultima_mensagem DESC
            """, (usuario_id, usuario_id, usuario_id))
            seguindo_lista = cursor.fetchall()

            # BUSCA QUEM ME SEGUE
            cursor.execute("""
                SELECT u.id, u.username, u.fotos_perfil,
                    COALESCE(MAX(m.data_envio), '1900-01-01') as ultima_mensagem
                FROM users u
                JOIN seguindo s1 ON u.id = s1.id_seguindo
                JOIN seguindo s2 ON u.id = s2.id_seguidor AND s2.id_seguindo = s1.id_seguidor
                LEFT JOIN mensagens m ON
                    ((m.id_remetente = u.id AND m.id_destinatario = %s) OR
                    (m.id_destinatario = u.id AND m.id_remetente = %s))
                WHERE s1.id_seguidor = %s
                GROUP BY u.id, u.username, u.fotos_perfil
                ORDER BY ultima_mensagem DESC
            """, (usuario_id, usuario_id, usuario_id))
            seguidores_lista = cursor.fetchall()

            # SEGUIDORES MUTUOS = CONTATOS
            contatos = [usuario for usuario in seguindo_lista if usuario in seguidores_lista]

            for contato in contatos:
                
                # ULTIMAS MSG (TEXTO, MIDIA, HORA)
                cursor.execute("""
                    SELECT mensagem, caminho_arquivo, data_envio
                    FROM mensagens
                    WHERE (id_remetente = %s AND id_destinatario = %s)
                       OR (id_remetente = %s AND id_destinatario = %s)
                    ORDER BY data_envio DESC
                    LIMIT 1
                """, (usuario_id, contato['id'], contato['id'], usuario_id))
                ultima = cursor.fetchone()
                contato['ultima_mensagem'] = ultima['mensagem'] if ultima else ""
                contato['ultima_midia'] = ultima['caminho_arquivo'] if ultima else ""
                contato['ultima_hora'] = ultima['data_envio'].strftime('%H:%M') if ultima and ultima['data_envio'] else ""

                # MSG NAO LIDAS
                cursor.execute("""
                    SELECT COUNT(*) as nao_vistas
                    FROM mensagens
                    WHERE id_remetente = %s AND id_destinatario = %s AND data_visualizacao IS NULL
                """, (contato['id'], usuario_id))
                contato['nao_vistas'] = cursor.fetchone()['nao_vistas']

    finally:
        conexao.close()

    return contatos
# =============================================================
#  CONTA DE POST
# =============================================================
def contar_total_posts(cursor, usuario_id):
    cursor.execute("SELECT COUNT(*) AS total_posts FROM posts WHERE users_id = %s", (usuario_id,))
    resultado = cursor.fetchone()
    return resultado['total_posts'] if resultado else 0
from datetime import datetime
# =============================================================
#  VERIFICA SE E AMIGOS
# =============================================================
def verificar_seguidores_mutuos(usuario_a, usuario_b):
    conexao = criar_conexao()
    resultado = False
    try:
        with conexao.cursor() as cursor:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT 1 
                    FROM seguindo s1
                    JOIN seguindo s2 ON s1.id_seguidor = s2.id_seguindo AND s1.id_seguindo = s2.id_seguidor
                    WHERE s1.id_seguidor = %s AND s1.id_seguindo = %s
                )
            """, (usuario_a, usuario_b))
            resultado = cursor.fetchone()[0] == 1
    finally:
        conexao.close()
    return resultado
# =============================================================
#  CONTA OS SEGUIDORES E SEGUINDO
# =============================================================
def contar_seguidores_e_seguindo(cursor, usuario_id):
    cursor.execute(
        "SELECT COUNT(*) AS seguidores_count FROM seguindo WHERE id_seguindo = %s",
        (usuario_id,)
    )
    seguidores_count = cursor.fetchone()['seguidores_count'] or 0

    cursor.execute(
        "SELECT COUNT(*) AS seguindo_count FROM seguindo WHERE id_seguidor = %s",
        (usuario_id,)
    )
    seguindo_count = cursor.fetchone()['seguindo_count'] or 0

    return seguidores_count, seguindo_count
# =============================================================
#  LISTA DE SEGUIDORES E SEGUINDO
# =============================================================
def obter_seguidores_e_seguindo(cursor, usuario_id):
    cursor.execute("""
        SELECT u.id, u.username, u.fotos_perfil
        FROM users u
        JOIN seguindo s ON u.id = s.id_seguidor
        WHERE s.id_seguindo = %s
    """, (usuario_id,))
    seguidores_lista = cursor.fetchall()

    cursor.execute("""
        SELECT u.id, u.username, u.fotos_perfil
        FROM users u
        JOIN seguindo s ON u.id = s.id_seguindo
        WHERE s.id_seguidor = %s
    """, (usuario_id,))
    seguindo_lista = cursor.fetchall()

    return {
        "seguidores_lista": seguidores_lista,
        "seguindo_lista": seguindo_lista
    }
# =============================================================
#  PARA SALVAR AS PESQUISAS
# =============================================================
def registrar_pesquisa_post(cursor, conexao, usuario_id: int, termo: str) -> None:

    termo = termo.strip()
    if len(termo) < 2:
        return 

    cursor.execute("""
        INSERT INTO historico_pesquisa_post (usuario_id, termo)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE criado_em = NOW()
    """, (usuario_id, termo))
    conexao.commit()
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
def render_swal_alert(script):
    return render_template_string(f"""
        <!DOCTYPE html>
        <html lang="pt-br">
        <head>
            <meta charset="UTF-8">
            <script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>
            <link rel="stylesheet" href="../static/css/style1.css" />
            <title>Alerta</title>
        </head>
        <body>
            {script}
        </body>
        </html>
    """)
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

def buscar_info_usuario_logado2(cursor, usuario_id):
    cursor.execute("SELECT fotos_perfil, username, tema FROM users WHERE id = %s", (usuario_id,))
    usuario = cursor.fetchone()

    nome = usuario['username'] if usuario else "Usuário"
    foto_perfil = usuario['fotos_perfil'] if usuario and usuario['fotos_perfil'] else url_for('static', filename='img/icone/user.png')
    tema = usuario['tema'] if usuario and usuario.get('tema') else 'claro'

    return nome, foto_perfil, tema

def buscar_info_usuario_logado_chat(usuario_id):
    conexao = criar_conexao()
    try:
        with conexao.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT fotos_perfil, audio_notificacoes_mensagem, tema 
                FROM users 
                WHERE id = %s
            """, (usuario_id,))
            usuario = cursor.fetchone()
    finally:
        conexao.close()

    foto_perfil = usuario['fotos_perfil'] if usuario and usuario['fotos_perfil'] else url_for('static', filename='img/icone/user.png')
    audio_notificacoes_mensagem = usuario['audio_notificacoes_mensagem'] if usuario and usuario['audio_notificacoes_mensagem'] is not None else True
    tema = usuario['tema'] if usuario and 'tema' in usuario else 'claro'

    return foto_perfil, audio_notificacoes_mensagem, tema
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
        LIMIT 6
    """)
    return cursor.fetchall()
# =============================================================
#  MENCIONAR USUARIO EM POST
# =============================================================
def extrair_mencoes(texto):
    """Extrai nomes de usuário mencionados com @ em um texto."""
    return set(re.findall(r'@([A-Za-z0-9_.-]+)', texto or ""))

def replace_mentions(text):
    if not text:
        return ""
    mention_pattern = re.compile(r'(?<!\w)@([A-Za-z0-9_.-]+)')
    def replace_match(match):
        username = match.group(1)
        return f'<a href="/obter_id_usuario?username={username}" class="mention-link" data-username="{username}">@{username}</a>'
    safe_text = Markup.escape(text)
    return Markup(mention_pattern.sub(replace_match, safe_text))

# Função replace_mentions_com_id que recebe texto e mapa_mencoes
def replace_mentions_com_id(text, mapa_mencoes):
    mention_pattern = re.compile(r'(?<!\w)@([A-Za-z0-9_.-]+)')
    def replace_match(match):
        username = match.group(1).lower()
        user_id = mapa_mencoes.get(username)
        if user_id:
            return f'<a href="/info-user/{user_id}" class="mention-link" data-id="{user_id}">@{username}</a>'
        return f'@{username}'
    safe_text = Markup.escape(text or "")
    return Markup(mention_pattern.sub(replace_match, safe_text))
# =============================================================
#  FORMATAR A DATA DO POST E NUMERO DO POST E DE MENSAGENS
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
    
def formatar_numero_curto(numero):
    try:
        numero = float(numero)
    except (ValueError, TypeError):
        return str(numero)

    if numero >= 1_000_000_000:
        return f"{numero / 1_000_000_000:.1f}B".rstrip('0').rstrip('.')
    elif numero >= 1_000_000:
        return f"{numero / 1_000_000:.1f}M".rstrip('0').rstrip('.')
    elif numero >= 1_000:
        return f"{numero / 1_000:.1f}K".rstrip('0').rstrip('.')
    else:
        return str(int(numero))

def formatar_data_mensagens(data):
    hoje = datetime.now().date()
    ontem = hoje - timedelta(days=1)

    if data.date() == hoje:
        return "Hoje"
    elif data.date() == ontem:
        return "Ontem"
    else:
        # Dicionário para mapear números de meses para nomes
        meses = {
            1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
            5: "maio", 6: "junho", 7: "julho", 8: "agosto",
            9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
        }

        # Extrai o dia, mês e ano
        dia = data.day
        mes = meses[data.month]
        ano = data.year

        # Retorna a data formatada
        return f"{dia} de {mes} de {ano}"

def data_msg(mensagens):
    for mensagem in mensagens:
        # Formata a hora (ex: "14:35")
        mensagem['data_envio'] = mensagem['data_envio'].strftime('%H:%M')

        # Converte a data (que veio em string 'YYYY-MM-DD') para datetime e formata com a função desejada
        data_dia = datetime.strptime(str(mensagem['data_dia']), '%Y-%m-%d')
        mensagem['data_dia'] = formatar_data_mensagens(data_dia)

    return mensagens
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

    # Extrair todas as menções dos comentários
    todas_mencoes = set()
    for comentario in comentarios:
        todas_mencoes.update(re.findall(r'(?<!\w)@([A-Za-z0-9_.-]+)', comentario['comentario']))

    mapa_mencoes = {}
    if todas_mencoes:
        formato = ','.join(['%s'] * len(todas_mencoes))
        cursor.execute(f"SELECT id, username FROM users WHERE username IN ({formato})", tuple(todas_mencoes))
        resultados = cursor.fetchall()
        for row in resultados:
            mapa_mencoes[row['username'].lower()] = row['id']


    # Processar cada comentário para formatar data, foto e substituir menções
    for comentario in comentarios:
        comentario['data_comentario'] = formatar_data(comentario['data_comentario'])
        if not comentario['fotos_perfil']:
            comentario['fotos_perfil'] = url_for('static', filename='img/icone/user.png')
        if 'parent_usuario_id' not in comentario or comentario['parent_usuario_id'] is None:
            comentario['parent_usuario_id'] = None
            comentario['parent_username'] = None

        # Substituir menções no texto do comentário
        comentario['comentario_com_mencoes'] = replace_mentions_com_id(comentario['comentario'], mapa_mencoes)

    return comentarios
# =============================================================
#  CONSULTA PARA PEGAR AS CURTIDAS E REPUBLICADOS E SALVADOS
# =============================================================
def buscar_total_curtidas(cursor, post_id):
    cursor.execute("""
        SELECT COUNT(*) as curtidas
        FROM curtidas 
        WHERE post_id = %s
    """, (post_id,))
    resultado = cursor.fetchone()
    return resultado['curtidas'] if resultado else 0

def buscar_total_republicados(cursor, post_id):
    cursor.execute("""
        SELECT COUNT(*) as posts_republicados
        FROM posts_republicados
        WHERE post_id = %s
    """, (post_id,))
    resultado = cursor.fetchone()
    return resultado['posts_republicados'] if resultado else 0

def buscar_total_salvos(cursor, post_id):
    cursor.execute("""
        SELECT COUNT(*) as posts_salvos
        FROM posts_salvos
        WHERE post_id = %s
    """, (post_id,))
    resultado = cursor.fetchone()
    return resultado['posts_salvos'] if resultado else 0
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
#  VERIFICA SE O USUARIO CURTIU O POST E REPUBLICOU E SALVOU
# =============================================================
def verificar_curtida(cursor, post_id, usuario_id):
    cursor.execute("""
        SELECT 1 FROM curtidas 
        WHERE post_id = %s AND usuario_id = %s
        LIMIT 1
    """, (post_id, usuario_id))
    return cursor.fetchone() is not None

def verificar_republicado(cursor, post_id, usuario_id):
    cursor.execute("""
        SELECT 1 FROM posts_republicados
        WHERE post_id = %s AND usuario_id = %s
        LIMIT 1
    """, (post_id, usuario_id))
    return cursor.fetchone() is not None

def verificar_salvos(cursor, post_id, usuario_id):
    cursor.execute("""
        SELECT 1 FROM posts_salvos
        WHERE post_id = %s AND usuario_id = %s
        LIMIT 1
    """, (post_id, usuario_id))
    return cursor.fetchone() is not None
# =============================================================
#  BUSCAR COMENTARIOS PUBLICO
# =============================================================
def buscar_config_comentarios_usuario(cursor, user_id):
    cursor.execute("""
        SELECT comentarios_publicos FROM users WHERE id = %s
    """, (user_id,))
    resultado = cursor.fetchone()
    return resultado['comentarios_publicos'] if resultado else 'todos'
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
    # BUSCAR TOP HASHTAGS
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

        # VERIFICA SE O POST TEM HASHTAGS POPULAR
        cursor.execute("SELECT hashtag_id FROM post_hashtags WHERE post_id = %s", (post_id,))
        hashtags_post = [row['hashtag_id'] for row in cursor.fetchall()]
        post['top_hashtag'] = any(h in top_hashtag_ids for h in hashtags_post)

        # CONTA A CURTIDA
        post['curtidas'] = buscar_total_curtidas(cursor, post['id'])

        # CONTA AS REPUBLICAÇÕES
        post['posts_republicados'] = buscar_total_republicados(cursor, post['id'])

        # CONTA OS SALVOS
        post['posts_salvos'] = buscar_total_salvos(cursor, post['id'])

        # CONTA AS VISUALIZAÇÕES
        post['visualizacoes'] = buscar_total_visualizacoes(cursor, post_id)

        # SE O USER CURTIU
        post['curtido_pelo_usuario'] = verificar_curtida(cursor, post['id'], usuario_id)

        # SE O USER REPUBLICOU
        post['republicado_pelo_usuario'] = verificar_republicado(cursor, post['id'], usuario_id)

        # SE O USER SALVOU
        post['salvo_pelo_usuario'] = verificar_salvos(cursor, post['id'], usuario_id)

        # SE OS COMENTÁRIOS SÃO PÚBLICOS
        post['comentarios_publicos'] = buscar_config_comentarios_usuario(cursor, post['users_id'])

        # verificar se são seguidores mútuos
        if post['comentarios_publicos'] == 'seguidores_mutuos':
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM seguindo 
                    WHERE id_seguidor = %s AND id_seguindo = %s
                ) AS segue,
                EXISTS(
                    SELECT 1 FROM seguindo 
                    WHERE id_seguidor = %s AND id_seguindo = %s
                ) AS seguido_por
            """, (usuario_id, post['users_id'], post['users_id'], usuario_id))
            res = cursor.fetchone()
            post['seguidores_mutuos'] = res['segue'] and res['seguido_por']
        else:
            post['seguidores_mutuos'] = False

        # SE O USER SEGUE O DONO DO POST
        cursor.execute("SELECT 1 FROM seguindo WHERE id_seguidor = %s AND id_seguindo = %s", (usuario_id, post['users_id']))
        post['seguindo'] = cursor.fetchone() is not None

        # COMENTÁRIOS
        post['comentarios'] = buscar_comentarios_post(cursor, post_id)

        # ======= SUBSTITUIR MENÇÕES PELO LINK COM ID FIXO =======
        cursor.execute("""
            SELECT u.username, pm.user_mencionado_id
            FROM post_mencoes pm
            JOIN users u ON u.id = pm.user_mencionado_id
            WHERE pm.post_id = %s
        """, (post_id,))
        mencoes = cursor.fetchall()
        mapa_mencoes = {m['username']: m['user_mencionado_id'] for m in mencoes}

        post['conteudo_com_mencoes'] = replace_mentions_com_id(post['conteudo'], mapa_mencoes)

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
#  PARA O MODELO ML DE POST
# =============================================================
def aplicar_ranking_personalizado(posts, usuario_id, modelo_ml):
    import pandas as pd

    features_modelo = [
        'curtiu', 'comentou', 'segue_autor', 'perfil_publico',
        'curtidas_post', 'comentarios_post', 'tempo_post', 'top_hashtag',
        'posts_republicados',
        'ja_visto'
    ]

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
            'posts_republicados': int(post.get('posts_republicados', 0)),
            'ja_visto': int(post.get('ja_visto', 0)),
        }

    dados_features = [extrair_features_post(post, usuario_id) for post in posts]
    df = pd.DataFrame(dados_features)

    if df.empty:
        return posts

    # Garante a ordem correta das colunas
    df_modelo = df[features_modelo]

    scores = modelo_ml.predict_proba(df_modelo)[:, 1]

    # PESOS
    peso_score_ml = 2.5
    peso_curtidas = 2.0
    peso_comentarios = 2.5
    peso_seguindo = 1.8
    peso_frescor = 0.15
    peso_ja_visto = -3.0
    peso_republicados = 1.5

    for i, post in enumerate(posts):
        score_ml = scores[i]
        post['score_ml'] = round(score_ml, 4)

        curtidas = post.get('curtidas', 0)
        comentarios = post.get('comentarios_count', 0)
        seguindo = int(post.get('seguindo', False))
        tempo_post = post.get('tempo_post', 0)
        ja_visto = int(post.get('ja_visto', 0))
        republicados = int(post.get('posts_republicados', 0))

        frescor = max(0, (24 - tempo_post)) * peso_frescor

        post['score_total'] = round(
            score_ml * peso_score_ml +
            curtidas * peso_curtidas +
            comentarios * peso_comentarios +
            seguindo * peso_seguindo +
            frescor +
            ja_visto * peso_ja_visto +
            republicados * peso_republicados, 4
        )

    posts.sort(key=lambda x: x['score_total'], reverse=True)
    return posts
# =============================================================
#  PARA A SUGESTOES DE PERFIL
# =============================================================
def buscar_sugestoes_perfis(cursor, usuario_id, limite=10):
    query = """
    SELECT DISTINCT 
      u.id, u.username, u.fotos_perfil, u.perfil_publico,
      (
          SELECT COUNT(*)
          FROM seguindo s1
          JOIN seguindo s2 ON s1.id_seguindo = s2.id_seguindo
          WHERE s1.id_seguidor = %(id)s AND s2.id_seguidor = u.id
      ) AS amigos_em_comum,
      EXISTS (
          SELECT 1
          FROM curtidas c
          JOIN posts p ON c.post_id = p.id
          WHERE c.usuario_id = %(id)s AND p.users_id = u.id
      ) AS curtiu_post,
      (u.data_cadastro >= NOW() - INTERVAL 5 DAY) AS perfil_recente
    FROM users u
    WHERE u.id != %(id)s
      AND u.suspenso = 0
      AND u.perfil_publico = 1
      AND NOT EXISTS (
          SELECT 1 FROM seguindo s 
          WHERE s.id_seguidor = %(id)s AND s.id_seguindo = u.id
      )
      AND NOT EXISTS (
          SELECT 1 FROM bloqueados b 
          WHERE b.usuario_id = %(id)s AND b.bloqueado_id = u.id
      )
    ORDER BY RAND()
    LIMIT %(limite)s
    """
    cursor.execute(query, {"id": usuario_id, "limite": limite})
    return cursor.fetchall()
# =============================================================
#  PARA O MODELO ML DE PERFIL
# =============================================================
def aplicar_pesos_e_ordenar_sugestoes_perfil(perfis):
    pesos = {
        'amigos_em_comum': 3.0,
        'curtiu_post': 2.5,
        'perfil_recente': 1.5
    }

    for perfil in perfis:
        score = 0
        score += pesos['amigos_em_comum'] * perfil['amigos_em_comum']
        score += pesos['curtiu_post'] * perfil['curtiu_post']
        score += pesos['perfil_recente'] * perfil['perfil_recente']
        perfil['score'] = score

    perfis.sort(key=lambda x: x['score'], reverse=True)
    return perfis
