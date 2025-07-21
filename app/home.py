from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
from app.conexao import criar_conexao
from app.utils import replace_mentions, aplicar_pesos_e_ordenar_sugestoes_perfil ,buscar_sugestoes_perfis, replace_hashtags, render_swal_alert, processar_posts, buscar_hashtags_mais_usadas, buscar_info_usuario_logado_1, verificar_seguindo_postindividual, aplicar_ranking_personalizado, gerar_filtros_busca, registrar_pesquisa_post
import pickle

home_bp = Blueprint('home', __name__)

# =============================================================
#  MODELO ALGORITMO TREINADO
# =============================================================
with open('modelo_algoritmo/modelo_feed.pkl', 'rb') as f:
    modelo_ml = pickle.load(f)

with open('modelo_algoritmo/modelo_perfis.pkl', 'rb') as f:
    modelo_perfis = pickle.load(f)
# =============================================================
#  FUNÇÕES
# =============================================================
@home_bp.app_template_filter('replace_mentions')
def _replace_mentions(text):
    return replace_mentions(text)

@home_bp.app_template_filter('replace_hashtags')
def _replace_hashtags(text):
    return replace_hashtags(text)
# =============================================================
#  PAGINA DO HOME COM ML
# =============================================================
@home_bp.route('/home')
def home():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # INFORMAÇÕES DO USUÁRIO LOGADO
                foto_perfil, nome_usuario, tema = buscar_info_usuario_logado_1(cursor, usuario_id)

                # SUGESTOES DE PERFIL
                sugestoes_perfis = buscar_sugestoes_perfis(cursor, usuario_id)

                # MODELO ML DE SUGESTOES
                sugestoes_perfis = aplicar_pesos_e_ordenar_sugestoes_perfil(sugestoes_perfis)

                # CONSULTA DOS POSTS
                cursor.execute("""
                    SELECT DISTINCT 
                        posts.id,
                        posts.*,
                        users.username,
                        users.fotos_perfil,
                        users.perfil_publico,
                        users.curtidas_publicas,
                        (
                            SELECT 1 
                            FROM seguindo 
                            WHERE id_seguidor = %s AND id_seguindo = posts.users_id
                            LIMIT 1
                        ) IS NOT NULL AS seguindo,
                        (
                            SELECT COUNT(*) 
                            FROM comentarios 
                            WHERE comentarios.post_id = posts.id
                        ) AS comentarios_count,
                        (
                            SELECT 1 
                            FROM visualizacoes 
                            WHERE visualizacoes.post_id = posts.id 
                            AND visualizacoes.usuario_id = %s
                            LIMIT 1
                        ) IS NOT NULL AS ja_visto
                    FROM posts
                    JOIN users ON posts.users_id = users.id
                    WHERE 
                        users.suspenso = 0
                        AND NOT EXISTS (
                            SELECT 1 
                            FROM bloqueados 
                            WHERE usuario_id = %s AND bloqueado_id = posts.users_id
                        )
                        AND NOT EXISTS (
                            SELECT 1 
                            FROM bloqueados 
                            WHERE usuario_id = posts.users_id AND bloqueado_id = %s
                        )
                        AND (
                            users.perfil_publico = 1
                            OR posts.users_id = %s
                            OR EXISTS (
                                SELECT 1 
                                FROM seguindo 
                                WHERE id_seguidor = %s AND id_seguindo = posts.users_id
                            )
                        )
                    ORDER BY posts.data_postagem DESC
                """, (usuario_id, usuario_id, usuario_id, usuario_id, usuario_id, usuario_id))

                posts = cursor.fetchall()

                # HASHTAG DO MOMENTO
                hashtags_top = buscar_hashtags_mais_usadas(cursor)

                # PROCESSAMENTO DO POST
                posts = processar_posts(posts, usuario_id, cursor)

                # MACHINE LEARNING
                posts = aplicar_ranking_personalizado(posts, usuario_id, modelo_ml)

            conexao.close()

            return render_template('home.html',
                                   posts=posts,
                                   usuario_id=usuario_id,
                                   foto_perfil=foto_perfil,
                                   nome_usuario=nome_usuario,
                                   hashtags_top=hashtags_top,
                                   tema=tema,
                                   sugestoes_perfis=sugestoes_perfis)

        return "Erro na conexão com o banco de dados."

    except Exception as e:
        return f"Erro ao conectar ao banco de dados: {str(e)}"
# =============================================================
#  PAGINA DO HOME PARA PESQUISAR POST ML
# ============================================================= 
@home_bp.route('/pesquisar', methods=['GET'])
def pesquisar():

    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    query          = request.args.get('query', '').strip()
    filtro         = request.args.get('filtro', 'mais_recente')
    tipo_conteudo  = request.args.get('tipo_conteudo', 'geral')

    
    if not query:
        return redirect(url_for('home.home'))

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()
        if not conexao:
            return "Erro na conexão com o banco de dados."

        with conexao.cursor(dictionary=True) as cursor:
            # INFORMACOES DO USUARIO LOGADO
            foto_perfil, nome_usuario, tema = buscar_info_usuario_logado_1(cursor, usuario_id)

            # SUGESTOES DE PERFIL
            sugestoes_perfis = buscar_sugestoes_perfis(cursor, usuario_id)

            # MODELO ML DE SUGESTOES
            sugestoes_perfis = aplicar_pesos_e_ordenar_sugestoes_perfil(sugestoes_perfis)

            # FILTRO
            order_by, filtro_tipo = gerar_filtros_busca(filtro, tipo_conteudo)

            # QUAIS POST DEVE MOSTRAR
            cursor.execute(f"""
                SELECT 
                    posts.*, 
                    users.username, 
                    users.fotos_perfil, 
                    users.curtidas_publicas,
                    users.perfil_publico,
                    
                    -- Se o usuário logado segue o autor do post:
                    (
                        SELECT 1 
                        FROM seguindo 
                        WHERE id_seguidor = %s AND id_seguindo = posts.users_id
                        LIMIT 1
                    ) IS NOT NULL AS seguindo,

                    -- Comentários
                    (
                        SELECT COUNT(*) 
                        FROM comentarios 
                        WHERE comentarios.post_id = posts.id
                    ) AS comentarios_count,

                    -- Curtidas
                    (
                        SELECT COUNT(*) 
                        FROM curtidas    
                        WHERE curtidas.post_id = posts.id
                    ) AS curtidas,

                    -- Já foi visto?
                    (
                        SELECT 1
                        FROM visualizacoes
                        WHERE visualizacoes.post_id = posts.id 
                        AND visualizacoes.usuario_id = %s
                        LIMIT 1
                    ) IS NOT NULL AS ja_visto

                FROM posts
                JOIN users ON posts.users_id = users.id

                WHERE 
                    (posts.conteudo LIKE %s OR users.username LIKE %s)
                    AND users.suspenso = 0

                    AND NOT EXISTS (
                        SELECT 1 FROM bloqueados
                        WHERE usuario_id = %s AND bloqueado_id = posts.users_id
                    )
                    AND NOT EXISTS (
                        SELECT 1 FROM bloqueados
                        WHERE usuario_id = posts.users_id AND bloqueado_id = %s
                    )

                    AND (
                        users.perfil_publico = 1
                        OR posts.users_id = %s
                        OR EXISTS (
                            SELECT 1 FROM seguindo
                            WHERE id_seguidor = %s AND id_seguindo = posts.users_id
                        )
                    )

                {filtro_tipo}
                {order_by}
            """, (
                usuario_id,               
                usuario_id,             
                f"%{query}%", f"%{query}%",
                usuario_id, usuario_id,    
                usuario_id, usuario_id    
            ))

            posts = cursor.fetchall()

            # SALVAR PESQUISA
            registrar_pesquisa_post(cursor, conexao, usuario_id, query)

            cursor.execute("""
                SELECT termo
                FROM historico_pesquisa_post
                WHERE usuario_id = %s
                ORDER BY criado_em DESC
                LIMIT 10
            """, (usuario_id,))
            historico_termos = [row['termo'] for row in cursor.fetchall()]

            # HASHTAG DO MOMENTO
            hashtags_top = buscar_hashtags_mais_usadas(cursor)

            # FOR DE POST
            posts = processar_posts(posts, usuario_id, cursor)

            # === MODELO ML ===
            if filtro == 'relevancia':
                posts = aplicar_ranking_personalizado(posts, usuario_id, modelo_ml)

        return render_template(
            'home.html',
            posts=posts,
            usuario_id=usuario_id,
            query=query,
            filtro=filtro,
            foto_perfil=foto_perfil,
            nome_usuario=nome_usuario,
            hashtags_top=hashtags_top,
            tipo_conteudo=tipo_conteudo,
            tema=tema,
            historico_termos=historico_termos,
            sugestoes_perfis=sugestoes_perfis  
        )

    except Exception as e:
        return f"Erro ao conectar ao banco de dados: {str(e)}"
# =============================================================
#  PAGINA PARA MOSTRAR POST ESPECIFICO
# =============================================================      
@home_bp.route('/post/<int:post_id>')
def post_individual(post_id):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))  

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()

        if not conexao:
            return "Erro na conexão com o banco de dados."

        with conexao.cursor(dictionary=True) as cursor:
            # INFORMACOES DO USUARIO LOGADO
            foto_perfil, nome_usuario, tema = buscar_info_usuario_logado_1(cursor, usuario_id)

            # SUGESTOES DE PERFIL
            sugestoes_perfis = buscar_sugestoes_perfis(cursor, usuario_id)

            # MODELO ML DE SUGESTOES
            sugestoes_perfis = aplicar_pesos_e_ordenar_sugestoes_perfil(sugestoes_perfis)


            # POST ESPECIFICO
            cursor.execute("""
                SELECT 
                    posts.*, 
                    users.username, 
                    users.fotos_perfil, 
                    users.perfil_publico, 
                    users.curtidas_publicas, 
                    users.suspenso,
                    (SELECT COUNT(*) FROM comentarios WHERE comentarios.post_id = posts.id) AS comentarios_count,
                    (
                        SELECT 1 
                        FROM seguindo 
                        WHERE id_seguidor = %s AND id_seguindo = posts.users_id
                        LIMIT 1
                    ) IS NOT NULL AS seguindo
                FROM posts 
                JOIN users ON posts.users_id = users.id
                WHERE posts.id = %s
                AND users.suspenso = 0  
            """, (usuario_id, post_id))

            post = cursor.fetchone()

            # HASHTAG DO MOMENTO
            hashtags_top = buscar_hashtags_mais_usadas(cursor)

            # SE NAO EXISTER OU ESTIVER SUSPENSO VOLTA PARA O /HOME
            if not post:
                conexao.close()
                return render_swal_alert(f'''
                    <script>
                        Swal.fire({{
                            title: 'Post Indisponível',
                            text: 'Este post não está mais disponível.',
                            icon: 'warning',
                            confirmButtonText: 'Ok',
                            confirmButtonColor: '#a76ab6',
                            background: '#2d2a32',
                            color: '#e0e0e0'
                        }}).then(() => {{
                            window.location.href = "{url_for('home.home')}";
                        }});
                    </script>
                ''')
            # VERIFICAÇAO DE BLOQUEIO ENTRE OS USER
            cursor.execute("""
                SELECT * FROM bloqueados 
                WHERE (usuario_id = %s AND bloqueado_id = %s)
                OR (usuario_id = %s AND bloqueado_id = %s)
            """, (usuario_id, post['users_id'], post['users_id'], usuario_id))
            bloqueio = cursor.fetchone()

            if bloqueio:
                conexao.close()
                return render_template(
                    'post_individual.html', 
                    acesso_negado=True, 
                    mensagem="Você não pode visualizar este conteúdo.",
                    usuario_id=usuario_id,
                    foto_perfil=foto_perfil,
                    nome_usuario=nome_usuario,
                    post=None,
                    tema=tema,
                    hashtags_top=hashtags_top,
                    sugestoes_perfis=sugestoes_perfis
                )

            # VERIFICA SE PUBLICO OU PRIVADO E SE O USER SEGUI
            segue = None
            if post['perfil_publico'] == 0 and post['users_id'] != usuario_id:
                segue = verificar_seguindo_postindividual(cursor, usuario_id, post['users_id'])
                post['seguindo'] = segue

                if not segue:
                    conexao.close()
                    return render_template(
                        'post_individual.html', 
                        acesso_negado=True, 
                        mensagem="Você não tem permissão para ver este post.",
                        usuario_id=usuario_id,
                        foto_perfil=foto_perfil,
                        nome_usuario=nome_usuario,
                        post=None,
                        tema=tema,
                        hashtags_top=hashtags_top,
                        sugestoes_perfis=sugestoes_perfis
                    )

            # Preparar lista para processar (função espera lista)
            posts = [post]

            # FOR DE POST
            posts = processar_posts(posts, usuario_id, cursor)

            # PEGAR O POST ESPECIFICO
            post = posts[0] if posts else None

        conexao.close()

        return render_template(
            'post_individual.html', 
            post=post, 
            usuario_id=usuario_id, 
            foto_perfil=foto_perfil, 
            nome_usuario=nome_usuario,
            acesso_negado=False,
            hashtags_top=hashtags_top,
            tema=tema,
            sugestoes_perfis=sugestoes_perfis
        )

    except Exception as e:
        return f"Erro ao conectar ao banco de dados: {str(e)}"
# =============================================================
#  PARA BUSCAR SUGESTAO
# =============================================================     
@home_bp.route('/sugestoes_pesquisa')
def sugestoes_pesquisa():
    termo = request.args.get('termo', '').strip()

    if len(termo) < 1:
        return jsonify([])

    try:
        conexao = criar_conexao()
        with conexao.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT termo 
                FROM historico_pesquisa_post
                WHERE termo LIKE %s
                ORDER BY criado_em DESC
                LIMIT 7
            """, (f"{termo}%",))
            resultados = [row['termo'] for row in cursor.fetchall()]
        conexao.close()
        return jsonify(resultados)
    except Exception as e:
        print("Erro ao buscar sugestões:", e)
        return jsonify([])

