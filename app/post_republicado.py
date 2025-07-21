from flask import Blueprint, render_template, redirect, url_for, session, request
from app.utils import replace_mentions, aplicar_pesos_e_ordenar_sugestoes_perfil ,buscar_sugestoes_perfis, buscar_info_usuario_logado_1, aplicar_ranking_personalizado, buscar_hashtags_mais_usadas, processar_posts, gerar_filtros_busca, registrar_pesquisa_post
from app.conexao import criar_conexao
import pickle

republicado_post_bp = Blueprint('postrepublicado', __name__)
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
@republicado_post_bp.app_template_filter('replace_mentions')
def _replace_mentions(text):
    return replace_mentions(text)
# =============================================================
#  PAGINA DO POST CURTIDO SEM ML
# =============================================================
@republicado_post_bp.route('/post-republicados')
def postrepublicado():
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
                        (SELECT COUNT(*) FROM comentarios WHERE comentarios.post_id = posts.id) AS comentarios_count,
                        EXISTS (
                            SELECT 1 FROM seguindo 
                            WHERE id_seguidor = %s AND id_seguindo = posts.users_id
                        ) AS seguindo
                    FROM posts 
                    JOIN users ON posts.users_id = users.id
                    JOIN posts_republicados ON posts.id = posts_republicados.post_id
                    WHERE posts_republicados.usuario_id = %s
                    AND users.suspenso = 0
                    ORDER BY posts_republicados.data DESC
                """, (usuario_id, usuario_id))

                posts = cursor.fetchall()

                # HASHTAG DO MOMENTO
                hashtags_top = buscar_hashtags_mais_usadas(cursor)

                # FOR DO POST
                posts = processar_posts(posts, usuario_id, cursor)

            conexao.close()

            return render_template('post_republicados.html', posts=posts, 
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
#  PAGINA DO POST REPUBLICADO PARA PESQUISAR POST COM ML
# =============================================================
@republicado_post_bp.route('/pesquisar-post-republicado')
def pesquisar_post_republicado():
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
                        users.perfil_publico,  -- <-- ESSA LINHA ADICIONADA
                        (SELECT COUNT(*) FROM comentarios WHERE comentarios.post_id = posts.id) AS comentarios_count,
                        (SELECT COUNT(*) FROM curtidas WHERE curtidas.post_id = posts.id) AS curtidas,
                        EXISTS (
                            SELECT 1 FROM seguindo 
                            WHERE id_seguidor = %s AND id_seguindo = posts.users_id
                        ) AS seguindo
                    FROM posts 
                    JOIN users ON posts.users_id = users.id
                    JOIN posts_republicados ON posts.id = posts_republicados.post_id
                    WHERE posts_republicados.usuario_id = %s
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
                'post_republicados.html',
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
# =============================================================
#  PAGINA DO POST REPUBLICADO PARA USER NAO LOGADO POST COM ML
# =============================================================
@republicado_post_bp.route('/post-republicados/<int:id_usuario>')
def postrepublicado_usuario(id_usuario):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_logado = session['usuario_id']

    # SE O LOGADO E DONO
    if usuario_logado == id_usuario:
        return redirect(url_for('postrepublicado.postrepublicado'))

    try:
        conexao = criar_conexao()
        if not conexao:
            return "Erro na conexão com o banco de dados."

        with conexao.cursor(dictionary=True) as cursor:
            # VERIFICA SE O USER ESTA SUSPENSO OU NAO EXISTE
            cursor.execute("""
                SELECT perfil_publico, username
                FROM users
                WHERE id = %s AND suspenso = 0
            """, (id_usuario,))
            dono = cursor.fetchone()
            if not dono:
                # VERIFICA SE O USER ESTA SUSPENSO OU NAO EXISTE LEVA A ESSA PAG
                return redirect(url_for('info_user.info_user', id_usuario=id_usuario))

            username_dono = dono['username']

            # VERIFICA OS BLOQUEIO
            cursor.execute("""
                SELECT 1 FROM bloqueados
                WHERE usuario_id = %s AND bloqueado_id = %s
            """, (id_usuario, usuario_logado))
            dono_bloqueou_voce = cursor.fetchone()

            # VERIFICA OS BLOQUEIO
            cursor.execute("""
                SELECT 1 FROM bloqueados
                WHERE usuario_id = %s AND bloqueado_id = %s
            """, (usuario_logado, id_usuario))
            voce_bloqueou_dono = cursor.fetchone()

            # SE O PERFIL E PRIVADO
            segue_dono = None
            if dono['perfil_publico'] == 0:
                cursor.execute("""
                    SELECT 1 FROM seguindo
                    WHERE id_seguidor = %s AND id_seguindo = %s
                """, (usuario_logado, id_usuario))
                segue_dono = cursor.fetchone()

            # SE HA BLOQUEIOS LEVA A ESSA PAG
            if dono_bloqueou_voce or voce_bloqueou_dono or (dono['perfil_publico'] == 0 and not segue_dono):
                return redirect(url_for('info_user.info_user', id_usuario=id_usuario))

            # BUSCA A INFO DO USER
            foto_perfil, nome_usuario, tema = buscar_info_usuario_logado_1(cursor, usuario_logado)

            # SUGESTOES DE PERFIL
            sugestoes_perfis = buscar_sugestoes_perfis(cursor, usuario_logado)

            # MODELO ML DE SUGESTOES
            sugestoes_perfis = aplicar_pesos_e_ordenar_sugestoes_perfil(sugestoes_perfis)

            # BUSCA O POST
            cursor.execute("""
                SELECT  p.*,
                        u.username,
                        u.fotos_perfil,
                        p.users_id,
                        u.curtidas_publicas,
                        u.perfil_publico,
                        (SELECT COUNT(*) FROM comentarios c WHERE c.post_id = p.id) AS comentarios_count,
                        EXISTS (
                            SELECT 1 
                            FROM seguindo s 
                            WHERE s.id_seguidor = %s AND s.id_seguindo = p.users_id
                        ) AS seguindo
                FROM posts p
                JOIN users u ON p.users_id = u.id
                JOIN posts_republicados pr ON p.id = pr.post_id
                WHERE pr.usuario_id = %s AND u.suspenso = 0
                ORDER BY pr.data DESC
            """, (usuario_logado, id_usuario))

            posts = cursor.fetchall()

            if not posts:
                # SE NAO A POST REPUBLICADOS LEVA A ESSA PAGINA AQUI
                return redirect(url_for('info_user.info_user', id_usuario=id_usuario))

            hashtags_top = buscar_hashtags_mais_usadas(cursor)
            posts = processar_posts(posts, usuario_logado, cursor)

        conexao.close()

        return render_template(
            "info_user_2.html",
            posts=posts,
            usuario_id=usuario_logado,       
            usuario_exibido=id_usuario,    
            id_usuario=id_usuario,            
            username_dono=username_dono,
            foto_perfil=foto_perfil,
            nome_usuario=nome_usuario,
            hashtags_top=hashtags_top,
            tema=tema,
            sugestoes_perfis=sugestoes_perfis
        )

    except Exception as e:
        return f"Erro ao buscar republicações: {e}"
