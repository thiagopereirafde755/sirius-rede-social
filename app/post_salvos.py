from flask import Blueprint, render_template, redirect, url_for, session, request
from app.utils import replace_mentions, aplicar_pesos_e_ordenar_sugestoes_perfil ,buscar_sugestoes_perfis, buscar_info_usuario_logado_1, aplicar_ranking_personalizado, buscar_hashtags_mais_usadas, processar_posts, gerar_filtros_busca, registrar_pesquisa_post
from app.conexao import criar_conexao
import pickle

salvo_post_bp = Blueprint('postsalvo', __name__)
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
@salvo_post_bp.app_template_filter('replace_mentions')
def _replace_mentions(text):
    return replace_mentions(text)
# =============================================================
#  PAGINA DO POST SALVO SEM ML
# =============================================================
@salvo_post_bp.route('/post-salvo')
def postsalvo():
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
                        users.perfil_publico,  -- <--- adicionado aqui
                        (SELECT COUNT(*)               -- nº de comentários
                        FROM comentarios
                        WHERE comentarios.post_id = posts.id) AS comentarios_count,
                        (SELECT COUNT(*)               -- nº de curtidas (opcional)
                        FROM curtidas
                        WHERE curtidas.post_id = posts.id) AS curtidas,
                        EXISTS (                       -- você já segue o autor?
                            SELECT 1
                            FROM seguindo s
                            WHERE s.id_seguidor = %s        -- ← usuário logado
                            AND s.id_seguindo = posts.users_id
                        ) AS seguindo
                    FROM posts
                    JOIN users          ON posts.users_id = users.id
                    JOIN posts_salvos   ON posts.id       = posts_salvos.post_id
                    WHERE posts_salvos.usuario_id = %s    -- ← posts que EU salvei
                    AND users.suspenso = 0
                    ORDER BY posts_salvos.data DESC
                """, (
                    usuario_id,  
                    usuario_id   
                ))

                posts = cursor.fetchall()

                # HASHTAG DO MOMENTO
                hashtags_top = buscar_hashtags_mais_usadas(cursor)

                # FOR DO POST
                posts = processar_posts(posts, usuario_id, cursor)

            conexao.close()

            return render_template('post_salvos.html', posts=posts, 
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
#  PAGINA DO POST SALVO PARA PESQUISAR POST COM ML
# =============================================================
@salvo_post_bp.route('/pesquisar-post-salvo')
def pesquisar_post_salvo():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))  

    usuario_id = session['usuario_id']
    query = request.args.get('query', '').strip()
    filtro = request.args.get('filtro', 'mais_recente')  
    tipo_conteudo = request.args.get('tipo_conteudo', 'geral')

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
                order_by, filtro_tipo = gerar_filtros_busca(filtro, tipo_conteudo)

                # QUAIS POST DEVE MOSTRAR
                cursor.execute(f"""
                    SELECT
                        posts.*,
                        users.username,
                        users.fotos_perfil,
                        posts.users_id,
                        users.curtidas_publicas,
                        users.perfil_publico,   -- <--- adicionado aqui
                        (SELECT COUNT(*) FROM comentarios WHERE comentarios.post_id = posts.id) AS comentarios_count,
                        (SELECT COUNT(*) FROM curtidas WHERE curtidas.post_id = posts.id) AS curtidas,
                        EXISTS (
                            SELECT 1 FROM seguindo s
                            WHERE s.id_seguidor = %s AND s.id_seguindo = posts.users_id
                        ) AS seguindo
                    FROM posts
                    JOIN users ON posts.users_id = users.id
                    JOIN posts_salvos ON posts.id = posts_salvos.post_id
                    WHERE posts_salvos.usuario_id = %s
                    AND users.suspenso = 0
                    AND (posts.conteudo LIKE %s OR users.username LIKE %s)
                    {filtro_tipo} {order_by}
                """, (
                    usuario_id,
                    usuario_id,
                    f"%{query}%",
                    f"%{query}%"
                ))

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
                'post_salvos.html',
                posts=posts,
                usuario_id=usuario_id,
                foto_perfil=foto_perfil,
                query=query,
                nome_usuario=nome_usuario,
                hashtags_top=hashtags_top,
                filtro=filtro,  
                tema=tema,
                tipo_conteudo=tipo_conteudo,
                sugestoes_perfis=sugestoes_perfis
            )
        
        return "Erro na conexão com o banco de dados."

    except Exception as e:
        return f"Erro ao conectar ao banco de dados: {str(e)}"