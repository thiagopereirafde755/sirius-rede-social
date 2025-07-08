import os
from flask import Blueprint, render_template, redirect, url_for, session, request, flash, Request, jsonify
from werkzeug.utils import secure_filename
from app.conexao import criar_conexao
from app.utils import replace_mentions, formatar_data, replace_hashtags, buscar_comentarios_post, processar_posts, buscar_hashtags_mais_usadas, extrair_features_post, buscar_comentarios_publicos, verificar_curtida, buscar_total_curtidas, buscar_info_usuario_logado_1, verificar_seguindo_postindividual, aplicar_ranking_personalizado, gerar_filtros_busca
from datetime import datetime
import pickle
import pandas as pd

home_bp = Blueprint('home', __name__)

# =============================================================
#  MODELO ALGORITMO TREINADO
# =============================================================
with open('modelo_algoritmo/modelo_feed.pkl', 'rb') as f:
    modelo_ml = pickle.load(f)
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
                # INFORMAÇÃO DO USUARIO LOGADO
                foto_perfil, nome_usuario, tema = buscar_info_usuario_logado_1(cursor, usuario_id)

                # QUAIS POST DEVE MOSTRAR
                cursor.execute("""
    SELECT DISTINCT 
        posts.id,
        posts.*, 
        users.username, 
        users.fotos_perfil, 
        posts.users_id, 
        users.curtidas_publicas,
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
        NOT EXISTS (
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
""", (usuario_id, usuario_id, usuario_id, usuario_id, usuario_id))


                posts = cursor.fetchall()

                # HASHTAG DO MOMENTO
                hashtags_top = buscar_hashtags_mais_usadas(cursor)

                # FOR DO POST
                posts = processar_posts(posts, usuario_id, cursor)

                # === MODELO ML ===
                posts = aplicar_ranking_personalizado(posts, usuario_id, modelo_ml)

            conexao.close()

            return render_template('home.html',
                                   posts=posts,
                                   usuario_id=usuario_id,
                                   foto_perfil=foto_perfil,
                                   nome_usuario=nome_usuario,
                                   hashtags_top=hashtags_top,
                                   tema=tema)

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

    query = request.args.get('query', '').strip()
    filtro = request.args.get('filtro', 'mais_recente')
    tipo_conteudo = request.args.get('tipo_conteudo', 'geral')

    if not query:
        return redirect(url_for('home.home'))

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()

        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # INFORMACOES DO USUARIO LOGADO
                foto_perfil, nome_usuario, tema = buscar_info_usuario_logado_1(cursor, usuario_id)

                # FILTRO
                order_by, filtro_tipo = gerar_filtros_busca(filtro, tipo_conteudo)

                # QUERY
                cursor.execute(f"""
                    SELECT posts.*, users.username, users.fotos_perfil, users.curtidas_publicas,
                        (SELECT COUNT(*) FROM comentarios WHERE comentarios.post_id = posts.id) AS comentarios_count,
                        (SELECT COUNT(*) FROM curtidas WHERE curtidas.post_id = posts.id) AS curtidas
                    FROM posts 
                    JOIN users ON posts.users_id = users.id
                    WHERE (posts.conteudo LIKE %s OR users.username LIKE %s)
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
                """, (f"%{query}%", f"%{query}%", usuario_id, usuario_id, usuario_id, usuario_id))
                posts = cursor.fetchall()

                # HASHTAG DO MOMENTO
                hashtags_top = buscar_hashtags_mais_usadas(cursor)

                # FOR DE POST
                posts = processar_posts(posts, usuario_id, cursor)

                # === MODELO ML ===
                if filtro == 'relevancia':
                    posts = aplicar_ranking_personalizado(posts, usuario_id, modelo_ml)

            conexao.close()

            return render_template('home.html', posts=posts,
                                   usuario_id=usuario_id,
                                   query=query,
                                   filtro=filtro,
                                   foto_perfil=foto_perfil,
                                   nome_usuario=nome_usuario,
                                   hashtags_top=hashtags_top,
                                   tipo_conteudo=tipo_conteudo,
                                   tema=tema)

        return "Erro na conexão com o banco de dados."

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

        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # INFORMACOES DO USUARIO LOGADO
                foto_perfil, nome_usuario, tema = buscar_info_usuario_logado_1(cursor, usuario_id)

                # BUSCA POST ESPECIFICO
                cursor.execute("""
                    SELECT posts.*, users.username, users.fotos_perfil, users.perfil_publico, users.curtidas_publicas,
                    (SELECT COUNT(*) FROM comentarios WHERE comentarios.post_id = posts.id) AS comentarios_count
                    FROM posts 
                    JOIN users ON posts.users_id = users.id
                    WHERE posts.id = %s
                """, (post_id,))
                post = cursor.fetchone()

                # HASHTAG DO MOMENTO
                hashtags_top = buscar_hashtags_mais_usadas(cursor)

                # SE NAO HOUVER POST LEVA PARA O /HOME
                if not post:
                    conexao.close()
                    return redirect(url_for('home.home'))

                # VERIFICACAO DE BLOQUEIO ENTRE USUARIOS
                cursor.execute("""
                    SELECT * FROM bloqueados 
                    WHERE (usuario_id = %s AND bloqueado_id = %s)
                    OR (usuario_id = %s AND bloqueado_id = %s)
                """, (usuario_id, post['users_id'], post['users_id'], usuario_id))
                bloqueio = cursor.fetchone()

                foto_perfil, nome_usuario, tema = buscar_info_usuario_logado_1(cursor, usuario_id)

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
                        hashtags_top=hashtags_top
                    )
                
                # PARA SABER SE O PERFIL E PUBLICO OU PRIVADO E O USER SEGUE OU NAO
                segue = None
                if post['perfil_publico'] == 0 and post['users_id'] != usuario_id:
                    
                    segue = verificar_seguindo_postindividual(cursor, usuario_id, post['users_id'])
                    post['seguindo'] = segue

                    foto_perfil, nome_usuario, tema = buscar_info_usuario_logado_1(cursor, usuario_id)

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
                            hashtags_top=hashtags_top
                        )

                # FORMATA DATA DO POST
                post['data_postagem'] = formatar_data(post['data_postagem'])
                # PEGA AS CURTIDAS
                post['curtidas'] = buscar_total_curtidas(cursor, post['id'])
                # VERIFICA SE O USUARIO CURTIU O POST
                post['curtido_pelo_usuario'] = verificar_curtida(cursor, post['id'], usuario_id)
                # VERIFICA SE OS COMENTARIOS SAO PUBLICOS
                post['comentarios_publicos'] = buscar_comentarios_publicos(cursor, post['users_id'])
                # COMENTARIOS
                post['comentarios'] = buscar_comentarios_post(cursor, post_id)

            conexao.close()
            return render_template(
                'post_individual.html', 
                post=post, 
                usuario_id=usuario_id, 
                foto_perfil=foto_perfil, 
                nome_usuario=nome_usuario,
                acesso_negado=False,
                hashtags_top=hashtags_top,
                tema=tema
            )
        
        return "Erro na conexão com o banco de dados."

    except Exception as e:
        return f"Erro ao conectar ao banco de dados: {str(e)}"