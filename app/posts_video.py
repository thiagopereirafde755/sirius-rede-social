from flask import Blueprint, render_template, redirect, url_for, session, request
from app.utils import replace_mentions, aplicar_pesos_e_ordenar_sugestoes_perfil ,buscar_sugestoes_perfis, buscar_info_usuario_logado_1, buscar_hashtags_mais_usadas, processar_posts, aplicar_ranking_personalizado, gerar_filtros_busca, registrar_pesquisa_post
from app.conexao import criar_conexao
import pickle

postesvideo_bp = Blueprint('post-video', __name__)

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
@postesvideo_bp.app_template_filter('replace_mentions')
def _replace_mentions(text):
    return replace_mentions(text)
# =============================================================
#  PAGINA DO POST VIDEO COM ML
# =============================================================
@postesvideo_bp.route('/post-video')
def video():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))  

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()

        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # INFORMAÇÃO DO USUARIO LOGADO
                foto_perfil, nome_usuario, tema = buscar_info_usuario_logado_1(cursor, usuario_id)

                # SUGESTOES DE PERFIL
                sugestoes_perfis = buscar_sugestoes_perfis(cursor, usuario_id)

                # MODELO ML DE SUGESTOES
                sugestoes_perfis = aplicar_pesos_e_ordenar_sugestoes_perfil(sugestoes_perfis)

                # QUAIS POST DEVE MOSTRAR
                cursor.execute("""
                    SELECT 
                        posts.*, 
                        users.username, 
                        users.fotos_perfil, 
                        posts.users_id, 
                        users.curtidas_publicas,
                        users.perfil_publico,
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
                        ) IS NOT NULL AS ja_visto,
                        EXISTS (
                            SELECT 1 
                            FROM seguindo 
                            WHERE id_seguidor = %s AND id_seguindo = posts.users_id
                        ) AS seguindo
                    FROM posts
                    JOIN users ON posts.users_id = users.id
                    WHERE posts.video IS NOT NULL 
                    AND posts.imagem IS NULL
                    AND users.suspenso = 0
                    ORDER BY posts.data_postagem DESC
                """, (usuario_id, usuario_id))

                posts = cursor.fetchall()

                # HASHTAG DO MOMENTO
                hashtags_top = buscar_hashtags_mais_usadas(cursor)

                # FOR DO POST
                posts = processar_posts(posts, usuario_id, cursor)

                # === MODELO ML ===
                posts = aplicar_ranking_personalizado(posts, usuario_id, modelo_ml)

            conexao.close()

            return render_template('videos.html', posts=posts, 
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
#  PAGINA DO POST VIDEO PARA PESQUISAR POST ML
# =============================================================
@postesvideo_bp.route('/pesquisa-video')
def pesquisar_video():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))  

    usuario_id = session['usuario_id']
    query = request.args.get('query', '').strip()
    filtro = request.args.get('filtro', 'mais_recente') 

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # INFORMACOES DO USUARIO LOGADO
                foto_perfil, nome_usuario, tema = buscar_info_usuario_logado_1(cursor, usuario_id)

                # SUGESTOES DE PERFIL
                sugestoes_perfis = buscar_sugestoes_perfis(cursor, usuario_id)

                # MODELO ML DE SUGESTOES
                sugestoes_perfis = aplicar_pesos_e_ordenar_sugestoes_perfil(sugestoes_perfis)

                # FILTRO
                order_by, filtro_tipo = gerar_filtros_busca(filtro, 'video')

                query_sql = f"""
                    SELECT 
                        posts.*, 
                        users.username, 
                        users.fotos_perfil, 
                        posts.users_id, 
                        users.curtidas_publicas,
                        users.perfil_publico,  -- <-- ADICIONADO AQUI
                        (SELECT COUNT(*) FROM comentarios WHERE comentarios.post_id = posts.id) AS comentarios_count,
                        (SELECT COUNT(*) FROM curtidas WHERE curtidas.post_id = posts.id) AS curtidas,
                        (
                            SELECT 1 
                            FROM visualizacoes 
                            WHERE visualizacoes.post_id = posts.id 
                            AND visualizacoes.usuario_id = %s
                            LIMIT 1
                        ) IS NOT NULL AS ja_visto,
                        EXISTS (
                            SELECT 1 
                            FROM seguindo 
                            WHERE id_seguidor = %s AND id_seguindo = posts.users_id
                        ) AS seguindo
                    FROM posts
                    JOIN users ON posts.users_id = users.id
                    WHERE 1=1
                    {filtro_tipo}
                    AND users.suspenso = 0
                    AND (posts.conteudo LIKE %s OR users.username LIKE %s)
                    {order_by}
                """
                cursor.execute(query_sql, (
                    usuario_id,      
                    usuario_id,       
                    f"%{query}%",    
                    f"%{query}%"     
                ))

                # PEGA OS POSTS ANTES DE FAZER QUALQUER OUTRO EXECUTE
                posts = cursor.fetchall()

                # SALVAR PESQUISA
                registrar_pesquisa_post(cursor, conexao, usuario_id, query)

                # HASHTAG DO MOMENTO
                hashtags_top = buscar_hashtags_mais_usadas(cursor)

                # FOR DE POST
                posts = processar_posts(posts, usuario_id, cursor)

                # === MODELO ML ===
                if filtro == 'relevancia':
                    posts = aplicar_ranking_personalizado(posts, usuario_id, modelo_ml)

            conexao.close()
            return render_template(
                'videos.html', 
                posts=posts, 
                usuario_id=usuario_id, 
                foto_perfil=foto_perfil, 
                query=query,  
                nome_usuario=nome_usuario,
                hashtags_top=hashtags_top,
                filtro=filtro,
                tema=tema,
                sugestoes_perfis=sugestoes_perfis  
            )
        return "Erro na conexão com o banco de dados."
    except Exception as e:
        return f"Erro ao conectar ao banco de dados: {str(e)}"