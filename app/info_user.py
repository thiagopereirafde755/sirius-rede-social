from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
from app.utils import replace_mentions, replace_hashtags, buscar_info_usuario_logado2, buscar_hashtags_mais_usadas, processar_posts, obter_seguidores_e_seguindo, contar_seguidores_e_seguindo, contar_total_posts
from app.conexao import criar_conexao

info_bp = Blueprint('info_user', __name__)

# =============================================================
#  FUNÇÕES
# =============================================================
@info_bp.app_template_filter('replace_mentions')
def _replace_mentions(text):
    return replace_mentions(text)

@info_bp.app_template_filter('replace_hashtags')
def _replace_hashtags(text):
    return replace_hashtags(text)
# =============================================================
#  PAGINA DE INFORMAÇÃO DE OUTRO USUARIO
# =============================================================
@info_bp.route('/info-user/<int:id_usuario>')
def info_user(id_usuario):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    if id_usuario == usuario_id:
        return redirect(url_for('inicio.inicio'))

    try:
        conexao = criar_conexao()
        if not conexao:
            return redirect(url_for('home.home'))

        with conexao.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id FROM users WHERE id = %s", (id_usuario,))
            if not cursor.fetchone():
                conexao.close()
                return redirect(url_for('home.home'))

            nome_usuario_logado, foto_perfil_logado, tema = buscar_info_usuario_logado2(cursor, usuario_id)

            cursor.execute("""
            INSERT INTO visualizacoes_perfis (usuario_id, perfil_id, data_visualizacao)
            VALUES (%s, %s, NOW())
            ON DUPLICATE KEY UPDATE data_visualizacao = NOW()
        """, (usuario_id, id_usuario))
            conexao.commit()

            # Verificação de bloqueio mútuo
            cursor.execute(
                "SELECT * FROM bloqueados WHERE usuario_id = %s AND bloqueado_id = %s",
                (usuario_id, id_usuario)
            )
            voce_bloqueou = cursor.fetchone()

            cursor.execute(
                "SELECT * FROM bloqueados WHERE usuario_id = %s AND bloqueado_id = %s",
                (id_usuario, usuario_id)
            )
            bloqueou_voce = cursor.fetchone()

            hashtags_top = buscar_hashtags_mais_usadas(cursor)

            if bloqueou_voce:
                cursor.execute("SELECT username FROM users WHERE id = %s", (id_usuario,))
                bloqueador = cursor.fetchone()
                conexao.close()
                return render_template('informacao-user.html',
                    usuario_bloqueou=True,
                    username_bloqueador=bloqueador['username'],
                    foto_perfil_logado=foto_perfil_logado,
                    nome_usuario_logado=nome_usuario_logado,
                    usuario_id=usuario_id,
                    foto_perfil=url_for('static', filename='img/icone/user.png'),
                    username="",
                    nome="",
                    bio="",
                    foto_capa=url_for('static', filename='img/icone/redes-sociais-capa-1.jpg'),
                    tema=tema,
                    hashtags_top=hashtags_top,
                )

            #  INFORMAÇÕES DO USUÁRIO VISITADO
            cursor.execute("""
                SELECT nome, username, fotos_perfil, bio, foto_capa,
                       perfil_publico, visibilidade_seguidores, suspenso
                FROM users WHERE id = %s
            """, (id_usuario,))
            usuario = cursor.fetchone()

            if not usuario:
                return "Usuário não encontrado."

            #  SE A CONTA ESTIVER SUSPENSA, mostra cartão e para tudo
            if usuario['suspenso']:
                conexao.close()
                return render_template('informacao-user.html',
                    conta_suspensa=True,
                    username_suspenso=usuario['username'],
                    foto_perfil_logado=foto_perfil_logado,
                    nome_usuario_logado=nome_usuario_logado,
                    usuario_id=usuario_id,
                    tema=tema,
                    hashtags_top=hashtags_top,
                )

            # VERIFICA SE O USER LOGADO SEGUI O VISITADO
            cursor.execute(
                "SELECT * FROM seguindo WHERE id_seguidor = %s AND id_seguindo = %s",
                (usuario_id, id_usuario)
            )
            usuario_segue = cursor.fetchone()

            visibilidade_seguidores = usuario['visibilidade_seguidores']
            perfil_publico = usuario['perfil_publico']
            mostrar_postagens = perfil_publico or usuario_segue

            total_posts = contar_total_posts(cursor, id_usuario)

            tem_republicacoes = False
            posts = []
            if mostrar_postagens:
                cursor.execute("""
                    SELECT  p.*, 
                            u.curtidas_publicas,
                            (SELECT COUNT(*) FROM comentarios WHERE comentarios.post_id = p.id) AS comentarios_count
                    FROM posts p
                    JOIN users u ON u.id = p.users_id
                    WHERE p.users_id = %s 
                    ORDER BY p.data_postagem DESC
                """, (id_usuario,))
                posts = cursor.fetchall()
                posts = processar_posts(posts, usuario_id, cursor)

            posts_republicados = []
            if mostrar_postagens:
                cursor.execute("""
                    SELECT pr.id AS republicacao_id, pr.data, 
                           p.*, 
                           u.username, u.fotos_perfil, u.curtidas_publicas,
                           (SELECT COUNT(*) FROM comentarios WHERE comentarios.post_id = p.id) AS comentarios_count
                    FROM posts_republicados pr
                    JOIN posts p ON pr.post_id = p.id
                    JOIN users u ON p.users_id = u.id
                    WHERE pr.usuario_id = %s
                    ORDER BY pr.data DESC
                """, (id_usuario,))
                posts_republicados = cursor.fetchall()
                posts_republicados = processar_posts(posts_republicados, usuario_id, cursor)
                tem_republicacoes = len(posts_republicados) > 0

            seguidores_count, seguindo_count = contar_seguidores_e_seguindo(cursor, id_usuario)
            listas = obter_seguidores_e_seguindo(cursor, id_usuario)
            seguidores_lista = listas['seguidores_lista']
            seguindo_lista = listas['seguindo_lista']

            cursor.execute(
                "SELECT * FROM pedidos_seguir WHERE id_solicitante = %s AND id_destino = %s",
                (usuario_id, id_usuario)
            )
            pedido_pendente = cursor.fetchone() is not None

            cursor.execute(
                "SELECT * FROM seguindo WHERE id_seguidor = %s AND id_seguindo = %s",
                (id_usuario, usuario_id)
            )
            usuario_te_segue = cursor.fetchone()

            cursor.execute("""
                SELECT u.id, u.nome, u.username, u.fotos_perfil
                FROM users u
                WHERE u.id IN (
                    SELECT s1.id_seguindo
                    FROM seguindo s1
                    JOIN seguindo s2 ON s1.id_seguindo = s2.id_seguidor
                    WHERE s1.id_seguidor = %s AND s2.id_seguindo = %s
                )
                AND u.id IN (
                    SELECT s1.id_seguindo
                    FROM seguindo s1
                    JOIN seguindo s2 ON s1.id_seguindo = s2.id_seguidor
                    WHERE s1.id_seguidor = %s AND s2.id_seguindo = %s
                )
            """, (usuario_id, usuario_id, id_usuario, id_usuario))
            amigos_mutuos = cursor.fetchall()
            amigos_mutuos_count = len(amigos_mutuos)

            data_amizade_iso = ""
            if usuario_segue and usuario_te_segue:
                data1 = usuario_segue['data_seguindo']
                data2 = usuario_te_segue['data_seguindo']
                data_amizade = max(data1, data2)
                data_amizade_iso = data_amizade.strftime('%Y-%m-%dT%H:%M:%S')

        conexao.close()

        return render_template('informacao-user.html',
            nome=usuario['nome'],
            username=usuario['username'],
            foto_perfil=usuario['fotos_perfil'] or url_for('static', filename='img/icone/user.png'),
            bio=usuario['bio'] or '',
            foto_capa=usuario['foto_capa'] or url_for('static', filename='img/icone/redes-sociais-capa-1.jpg'),
            posts=posts,
            posts_republicados=posts_republicados,
            usuario_segue=usuario_segue,
            id_usuario=id_usuario,
            data_amizade=data_amizade_iso,
            usuario_id=usuario_id,
            seguidores=seguidores_count,
            seguindo=seguindo_count,
            seguidores_lista=seguidores_lista,
            seguindo_lista=seguindo_lista,
            foto_userlog=foto_perfil_logado,
            total_posts=total_posts,
            pedido_pendente=pedido_pendente,
            perfil_publico=perfil_publico,
            mostrar_postagens=mostrar_postagens,
            nome_usuario_logado=nome_usuario_logado,
            foto_perfil_logado=foto_perfil_logado,
            usuario_te_segue=usuario_te_segue,
            visibilidade_seguidores=visibilidade_seguidores,
            voce_bloqueou=voce_bloqueou,
            tema=tema,
            hashtags_top=hashtags_top,
            tem_republicacoes=tem_republicacoes,
            username_bloqueado=usuario['username'],
            amigos_mutuos=amigos_mutuos,
            amigos_mutuos_count=amigos_mutuos_count
        )

    except Exception as e:
        print(f"Erro ao conectar ao banco de dados: {str(e)}")
        return redirect(url_for('home.home'))
# =============================================================
#  OBTER ID DO USUARIO
# =============================================================
@info_bp.route('/obter_id_usuario')
def obter_id_usuario():
    username = request.args.get('username')
    if not username:
        return jsonify({'error': 'Username não fornecido'}), 400
    
    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                usuario = cursor.fetchone()
                
                if usuario:
                    return jsonify({'id': usuario['id']})
                else:
                    return jsonify({'error': 'Usuário não encontrado'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        if 'conexao' in locals() and conexao:
            conexao.close()
    
    return jsonify({'error': 'Erro ao buscar usuário'}), 500

