from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, flash
from app.conexao import criar_conexao
from app.enviar_email import enviar_email_suspensao_user, enviar_email_remocao_mensagem ,enviar_email_remocao_suspensao_user, enviar_email_remocao_post, enviar_email_remocao_comentario, enviar_email_status_denuncia
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash

administrador_bp = Blueprint('administrador', __name__)

# =============================================================
#  LOGIN ADM
# =============================================================
@administrador_bp.route('/login_adm', methods=['GET', 'POST'])
def login_adm():
    if request.method == 'POST':
        user = request.form['user']
        senha = request.form['senha']

        conexao = criar_conexao()
        if conexao:
            try:
                with conexao.cursor(dictionary=True) as cursor:
                    cursor.execute("SELECT * FROM adm WHERE user = %s", (user,))
                    administrador = cursor.fetchone()

                    if administrador and check_password_hash(administrador['senha'], senha):
                        session['admin_id'] = administrador['id']
                        session['admin_user'] = administrador['user']
                        return redirect(url_for('administrador.pagina_inicial_admin'))
                    else:
                        return render_template('login_adm.html', erro="Usuário ou senha inválidos.")
            finally:
                conexao.close()
    return render_template('login_adm.html')
# =============================================================
#  DESLOGAR ADM
# =============================================================
@administrador_bp.route('/logout_adm')
def logout_adm():
    session.pop('admin_id', None)
    session.pop('admin_user', None)
    return redirect(url_for('administrador.login_adm'))
# =============================================================
#  PAGINA INICIAL DO ADM
# =============================================================
@administrador_bp.route('/pagina_inicial_admin')
def pagina_inicial_admin():
    if 'admin_id' not in session:
        return redirect(url_for('administrador.login_adm'))

    return render_template('pagina_inicial_admin.html')
# =============================================================
#  PAGINA PARA PODE ADMINISTRAR ADM
# =============================================================
@administrador_bp.route('/sessao_administrador')
def sessao_administrador():
    if 'admin_id' not in session:
        return redirect(url_for('administrador.login_adm'))

    termo_busca = request.args.get('q', '').strip()

    conexao = criar_conexao()
    administradores = []

    if conexao:
        try:
            with conexao.cursor(dictionary=True) as cursor:
                if termo_busca:
                    cursor.execute("""
                        SELECT id, user, senha FROM adm
                        WHERE user LIKE %s
                        ORDER BY id DESC
                    """, ('%' + termo_busca + '%',))
                else:
                    cursor.execute("SELECT id, user, senha FROM adm ORDER BY id DESC")

                administradores = cursor.fetchall()
        finally:
            conexao.close()

    return render_template('sessao_administrador.html', administradores=administradores)
# =============================================================
#  PARA PODER ADICIONAR ADIMINISTRADOR
# =============================================================
@administrador_bp.route('/adicionar_administrador', methods=['POST'])
def adicionar_administrador():
    if 'admin_id' not in session:
        return jsonify({'success': False, 'message': 'Sessão expirada'}), 401

    user = request.form['user']
    senha = request.form['senha']

    senha_hash = generate_password_hash(senha)

    conexao = criar_conexao()
    if conexao:
        try:
            with conexao.cursor() as cursor:
                cursor.execute("INSERT INTO adm (user, senha) VALUES (%s, %s)", (user, senha_hash))
                conexao.commit()
                return jsonify({'success': True, 'message': 'Administrador adicionado com sucesso!'})
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erro ao adicionar administrador: {str(e)}'}), 500
        finally:
            conexao.close()

    return jsonify({'success': False, 'message': 'Erro de conexão com o banco de dados'}), 500
# =============================================================
#  PARA PODER DELETAR ADIMINISTRADOR
# =============================================================
@administrador_bp.route('/deletar_administrador/<int:admin_id>')
def deletar_administrador(admin_id):
    if 'admin_id' not in session:
        return redirect(url_for('administrador.login_adm'))

    # NAO DEIXA ELE SE AUTO DELETAR
    if session['admin_id'] == admin_id:
        return redirect(url_for('administrador.sessao_administrador'))

    conexao = criar_conexao()
    if conexao:
        try:
            with conexao.cursor() as cursor:
                cursor.execute("DELETE FROM adm WHERE id = %s", (admin_id,))
                conexao.commit()
        finally:
            conexao.close()

    return redirect(url_for('administrador.sessao_administrador'))
# =============================================================
#  PARA PODER ATUALIZAR O ADIMINISTRADOR
# =============================================================
@administrador_bp.route('/atualizar_administrador', methods=['POST'])
def atualizar_administrador():
    if 'admin_id' not in session:
        return redirect(url_for('administrador.login_adm'))

    admin_id = request.form['id']
    user = request.form['user']

    conexao = criar_conexao()
    if conexao:
        try:
            with conexao.cursor() as cursor:
                cursor.execute("UPDATE adm SET user = %s, senha = %s WHERE id = %s", (user, admin_id))
                conexao.commit()
        finally:
            conexao.close()

    return redirect(url_for('administrador.sessao_administrador'))
# =============================================================
#  PAGINA USUARIOS ADM
# =============================================================
@administrador_bp.route('/sessao_usuarios')
def pagina_usuarios_admin():
    if 'admin_id' not in session:
        return redirect(url_for('administrador.login_adm'))

    query = request.args.get('q', '').strip()
    conexao = criar_conexao()
    usuarios = []

    if conexao:
        try:
            with conexao.cursor(dictionary=True) as cursor:
                if query:
                    cursor.execute("""
                        SELECT 
                            u.id,
                            u.nome,
                            u.username,
                            u.bio,
                            u.data_nascimento,
                            u.data_cadastro,
                            u.fotos_perfil,
                            u.foto_capa,
                            u.suspenso,
                            COUNT(p.id) AS total_posts
                        FROM users u
                        LEFT JOIN posts p ON u.id = p.users_id
                        WHERE u.username LIKE %s OR u.id = %s
                        GROUP BY u.id, u.nome, u.username, u.bio, u.data_nascimento, u.data_cadastro, u.fotos_perfil, u.foto_capa, u.suspenso
                        ORDER BY u.id DESC
                    """, (f"%{query}%", query if query.isdigit() else 0))
                else:
                    cursor.execute("""
                        SELECT 
                            u.id,
                            u.nome,
                            u.username,
                            u.bio,
                            u.data_nascimento,
                            u.data_cadastro,
                            u.fotos_perfil,
                            u.foto_capa,
                            u.suspenso,
                            COUNT(p.id) AS total_posts
                        FROM users u
                        LEFT JOIN posts p ON u.id = p.users_id
                        GROUP BY u.id, u.nome, u.username, u.bio, u.data_nascimento, u.data_cadastro, u.fotos_perfil, u.foto_capa, u.suspenso
                        ORDER BY u.id DESC
                    """)
                usuarios = cursor.fetchall()
        finally:
            conexao.close()

    return render_template('sessao_usuario_adm.html', usuarios=usuarios)
# =============================================================
#  SUSPENDE O USUARIO
# =============================================================
@administrador_bp.route('/suspender_usuario/<int:user_id>', methods=['POST'])
def suspender_usuario(user_id):
    if 'admin_id' not in session:
        return redirect(url_for('administrador.login_adm'))

    query = request.form.get('q', '')  

    conexao = criar_conexao()
    if not conexao:
        flash("Erro ao conectar ao banco.", "danger")
        return redirect(url_for('administrador.pagina_usuarios_admin', q=query))

    try:
        with conexao.cursor(dictionary=True) as cursor:
            cursor.execute("UPDATE users SET suspenso = 1 WHERE id = %s", (user_id,))
            conexao.commit()

            cursor.execute("SELECT email, username FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()

            if user:
                enviar_email_suspensao_user(user['email'], user['username'])

            flash("Usuário suspenso com sucesso.", "success")

    except Exception as e:
        print(f"Erro ao suspender usuário: {e}")
        flash("Erro ao suspender usuário.", "danger")

    finally:
        conexao.close()

    return redirect(url_for('administrador.pagina_usuarios_admin', q=query))
# =============================================================
#  REMOVE A SUSPENSÃO DO USUARIO
# =============================================================
@administrador_bp.route('/remover_suspensao_usuario/<int:user_id>', methods=['POST'])
def remover_suspensao_usuario(user_id):
    if 'admin_id' not in session:
        return redirect(url_for('administrador.login_adm'))

    query = request.form.get('q', '')

    conexao = criar_conexao()
    if not conexao:
        flash("Erro ao conectar ao banco.", "danger")
        return redirect(url_for('administrador.pagina_usuarios_admin', q=query))

    try:
        with conexao.cursor(dictionary=True) as cursor:
            cursor.execute("UPDATE users SET suspenso = 0 WHERE id = %s", (user_id,))
            conexao.commit()

            cursor.execute("SELECT email, username FROM users WHERE id = %s", (user_id,))
            user = cursor.fetchone()

            if user:
                enviar_email_remocao_suspensao_user(user['email'], user['username'])

            flash("Suspensão removida com sucesso.", "success")

    except Exception as e:
        print(f"Erro ao remover suspensão: {e}")
        flash("Erro ao remover suspensão.", "danger")

    finally:
        conexao.close()

    return redirect(url_for('administrador.pagina_usuarios_admin', q=query))
# =============================================================
#  REMOVE A SUSPENSÃO DO USUARIO
# =============================================================
@administrador_bp.route('/sessao_post')
def pagina_post_admin():
    if 'admin_id' not in session:
        return redirect(url_for('administrador.login_adm'))

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                termo_busca = request.args.get('q', '').strip()

                query = """
                    SELECT 
                        p.id AS post_id,
                        u.username,
                        p.conteudo,
                        p.imagem,
                        p.video,
                        p.data_postagem,
                        (SELECT COUNT(*) FROM curtidas WHERE post_id = p.id) AS qtd_curtidas,
                        (SELECT COUNT(*) FROM comentarios WHERE post_id = p.id) AS qtd_comentarios,
                        (SELECT COUNT(*) FROM visualizacoes WHERE post_id = p.id) AS qtd_visualizacoes,
                        (SELECT COUNT(*) FROM posts_republicados WHERE post_id = p.id) AS qtd_republicacoes,
                        (SELECT COUNT(*) FROM posts_salvos WHERE post_id = p.id) AS qtd_salvo
                    FROM posts p
                    JOIN users u ON p.users_id = u.id
                """

                parametros = []

                if termo_busca:
                    query += " WHERE u.username LIKE %s OR p.id = %s"
                    parametros = [f"%{termo_busca}%", termo_busca if termo_busca.isdigit() else 0]

                query += " ORDER BY p.data_postagem DESC"

                cursor.execute(query, parametros)
                posts = cursor.fetchall()

            return render_template('sessao_post_adm.html', posts=posts)

    except Exception as e:
        print(f"Erro ao buscar posts: {e}")
        flash("Erro ao carregar os posts.", "danger")
        return redirect(url_for('administrador.pagina_inicial_admin'))
# =============================================================
#  REMOVE POST
# =============================================================
@administrador_bp.route('/deletar_post/<int:post_id>', methods=['POST'])
def deletar_post(post_id):
    if 'admin_id' not in session:
        return redirect(url_for('administrador.login_adm'))

    try:
        conexao = criar_conexao()
        with conexao.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT users_id FROM posts WHERE id = %s", (post_id,))
            post = cursor.fetchone()

            if post:
                users_id = post['users_id']

                cursor.execute("SELECT email, username FROM users WHERE id = %s", (users_id,))
                user_info = cursor.fetchone()

                if user_info:
                    enviar_email_remocao_post(user_info['email'], user_info['username'])

                # NOTIFICACAO DE REMOÇÃO
                cursor.execute("""
                    INSERT INTO notificacoes (usuario_id, tipo, origem_usuario_id, lida)
                    VALUES (%s, 'post_removido', NULL, 0)
                """, (users_id,))

            cursor.execute("DELETE FROM notificacoes WHERE post_id = %s", (post_id,))
            cursor.execute("DELETE FROM visualizacoes WHERE post_id = %s", (post_id,))
            cursor.execute("DELETE FROM comentarios WHERE post_id = %s", (post_id,))
            cursor.execute("DELETE FROM curtidas WHERE post_id = %s", (post_id,))
            cursor.execute("DELETE FROM posts_salvos WHERE post_id = %s", (post_id,))
            cursor.execute("DELETE FROM posts_republicados WHERE post_id = %s", (post_id,))
            cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
            conexao.commit()

        flash("Post removido com sucesso!", "success")
    except Exception as e:
        print("Erro ao remover post:", e)
        flash("Erro ao remover post.", "danger")
    finally:
        if conexao:
            conexao.close()

    q = request.form.get('q', '')
    return redirect(url_for('administrador.pagina_post_admin', q=q))
# =============================================================
#  SESSAO COMENTARIOS ADM
# =============================================================
@administrador_bp.route('/sessao_comentarios_adm')
def pagina_sessao_comentarios_adm():
    if 'admin_id' not in session:
        return redirect(url_for('administrador.login_adm'))

    q = request.args.get('q', '').strip()
    try:
        conexao = criar_conexao()
        with conexao.cursor(dictionary=True) as cursor:
            if q:
                query = """
                    SELECT c.id, c.post_id, c.data_comentario, c.parent_comment_id, c.comentario,
                           u.username
                    FROM comentarios c
                    JOIN users u ON c.usuario_id = u.id
                    WHERE c.id LIKE %s OR c.post_id LIKE %s OR u.username LIKE %s
                    ORDER BY c.data_comentario DESC
                """
                cursor.execute(query, (f"%{q}%", f"%{q}%", f"%{q}%"))
            else:
                cursor.execute("""
                    SELECT c.id, c.post_id, c.data_comentario, c.parent_comment_id, c.comentario,
                           u.username
                    FROM comentarios c
                    JOIN users u ON c.usuario_id = u.id
                    ORDER BY c.data_comentario DESC
                """)
            comentarios = cursor.fetchall()
    except Exception as e:
        print("Erro ao buscar comentários:", e)
        comentarios = []
    finally:
        if conexao:
            conexao.close()

    return render_template('sessao_comentarios_adm.html', comentarios=comentarios)
# =============================================================
#  DELETAR COMENTARIO
# =============================================================
@administrador_bp.route('/deletar_comentario/<int:comentario_id>', methods=['POST'])
def deletar_comentario(comentario_id):
    if 'admin_id' not in session:
        return redirect(url_for('administrador.login_adm'))

    try:
        conexao = criar_conexao()
        with conexao.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT usuario_id FROM comentarios WHERE id = %s", (comentario_id,))
            comentario = cursor.fetchone()

            if comentario:
                usuario_id_do_comentario = comentario['usuario_id']

                cursor.execute("SELECT email, username FROM users WHERE id = %s", (usuario_id_do_comentario,))
                user_info = cursor.fetchone()

                if user_info:
                    enviar_email_remocao_comentario(user_info['email'], user_info['username'])

                cursor.execute("DELETE FROM comentarios WHERE id = %s", (comentario_id,))
                conexao.commit()

                cursor.execute("""
                    INSERT INTO notificacoes (usuario_id, tipo, comentario_id)
                    VALUES (%s, 'comentario_removido', %s)
                """, (usuario_id_do_comentario, comentario_id))
                conexao.commit()

                flash("Comentário removido com sucesso!", "success")
            else:
                flash("Comentário não encontrado.", "warning")

    except Exception as e:
        print("Erro ao deletar comentário:", e)
        flash("Erro ao remover comentário.", "danger")
    finally:
        if conexao:
            conexao.close()

    return redirect(request.referrer or url_for('administrador.pagina_sessao_comentarios_adm'))
# =============================================================
#  PAGINA DE DENUNCIAS
# =============================================================
@administrador_bp.route('/sessao_denuncias_adm')
def pagina_denuncia_admin():
    if 'admin_id' not in session:
        return redirect(url_for('administrador.login_adm'))

    q = request.args.get('q', '').strip()
    denuncias = []

    try:
        conexao = criar_conexao()
        with conexao.cursor(dictionary=True) as cursor:
            if q:
                cursor.execute("""
                    SELECT d.*, u.username AS denunciante
                    FROM denuncias d
                    JOIN users u ON d.id_denunciante = u.id
                    WHERE d.tipo LIKE %s
                    ORDER BY d.data_denuncia DESC
                """, (f"%{q}%",))
            else:
                cursor.execute("""
                    SELECT d.*, u.username AS denunciante
                    FROM denuncias d
                    JOIN users u ON d.id_denunciante = u.id
                    ORDER BY d.data_denuncia DESC
                """)
            denuncias = cursor.fetchall()
            status_lista = list({denuncia['status'] for denuncia in denuncias})
    except Exception as e:
        print("Erro ao buscar denúncias:", e)
        status_lista = []
    finally:
        if conexao:
            conexao.close()

    return render_template('sessao_denuncias_adm.html', denuncias=denuncias, status_lista=status_lista)
# =============================================================
#  PARA ALTERAR STATUS DA DENUNCIA
# =============================================================
@administrador_bp.route("/alterar_status_denuncia", methods=["POST"])
def alterar_status_denuncia():
    if "admin_id" not in session:
        return jsonify({"sucesso": False, "mensagem": "Acesso não autorizado."}), 401

    data = request.get_json()
    id_denuncia = data.get("id")
    novo_status = data.get("novo_status")

    status_possiveis = ("pendente", "em_analise", "resolvido", "ignorado")

    if novo_status not in status_possiveis:
        return jsonify({"sucesso": False, "mensagem": "Status inválido."}), 400

    conexao = None
    try:
        conexao = criar_conexao()
        with conexao.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT d.id_alvo, d.tipo, d.status AS status_atual, u.email, u.username
                  FROM denuncias d
                  JOIN users u ON u.id = d.id_denunciante
                 WHERE d.id = %s
            """, (id_denuncia,))
            denuncia = cursor.fetchone()
            if not denuncia:
                return jsonify({"sucesso": False, "mensagem": "Denúncia não encontrada."}), 404

            status_atual = denuncia['status_atual']

            transicoes_validas = {
                'pendente': ['em_analise'],
                'em_analise': ['resolvido', 'ignorado'],
                'resolvido': [],
                'ignorado': []
            }

            if novo_status == status_atual:
                return jsonify({"sucesso": False, "mensagem": "O status já está definido como esse."}), 400

            if novo_status not in transicoes_validas.get(status_atual, []):
                return jsonify({"sucesso": False, "mensagem": f"Transição inválida de '{status_atual}' para '{novo_status}'."}), 400

            cursor.execute(
                "UPDATE denuncias SET status = %s WHERE id = %s",
                (novo_status, id_denuncia)
            )
            conexao.commit()

        try:
            enviar_email_status_denuncia(
                email      = denuncia["email"],
                username   = denuncia["username"],
                tipo       = denuncia["tipo"],
                id_alvo    = denuncia["id_alvo"],
                novo_status= novo_status
            )
        except Exception as e:
            print(e)

        return jsonify({"sucesso": True})

    except Exception as e:
        print("Erro ao alterar status:", e)
        return jsonify({"sucesso": False, "mensagem": "Erro interno."}), 500
    finally:
        if conexao:
            conexao.close()
# =============================================================
#  PAGINA ESTATISTICAS DO ADM
# =============================================================
@administrador_bp.route('/sessao_estatisticas_adm')
def pagina_estatisticas_admin():
    if 'admin_id' not in session:
        return redirect(url_for('administrador.login_adm'))

    total_administradores = 0
    total_user = 0
    total_posts = 0
    total_comentarios = 0
    total_curtidas = 0
    total_views = 0
    total_msg = 0
    total_denuncias = 0

    try:
        conexao = criar_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM adm")
            resultado = cursor.fetchone()
            total_administradores = resultado[0] if resultado else 0

            cursor.execute("SELECT COUNT(*) FROM users")
            resultado = cursor.fetchone()
            total_user = resultado[0] if resultado else 0

            cursor.execute("SELECT COUNT(*) FROM posts")
            resultado = cursor.fetchone()
            total_posts = resultado[0] if resultado else 0

            cursor.execute("SELECT COUNT(*) FROM comentarios")
            resultado = cursor.fetchone()
            total_comentarios = resultado[0] if resultado else 0

            cursor.execute("SELECT COUNT(*) FROM curtidas")
            resultado = cursor.fetchone()
            total_curtidas = resultado[0] if resultado else 0

            cursor.execute("SELECT COUNT(*) FROM visualizacoes")
            resultado = cursor.fetchone()
            total_views = resultado[0] if resultado else 0

            cursor.execute("SELECT COUNT(*) FROM mensagens")
            resultado = cursor.fetchone()
            total_msg = resultado[0] if resultado else 0

            cursor.execute("SELECT COUNT(*) FROM denuncias")
            resultado = cursor.fetchone()
            total_denuncias = resultado[0] if resultado else 0

    except Exception as e:
        print("Erro ao buscar estatísticas:", e)

    finally:
        if conexao:
            conexao.close()

    return render_template(
        'sessao_estatisticas_adm.html',
        total_administradores=total_administradores,
        total_user=total_user,
        total_posts=total_posts,
        total_comentarios=total_comentarios,
        total_curtidas=total_curtidas,
        total_views=total_views,
        total_msg=total_msg,
        total_denuncias=total_denuncias
    )
# =============================================================
#  PAGINA DE SESSAO DE MENSAGENS
# =============================================================
@administrador_bp.route('/sessao_mensagens_adm')
def pagina_sessao_mensagens_adm():
    if 'admin_id' not in session:
        return redirect(url_for('administrador.login_adm'))

    q = request.args.get('q', '').strip()
    conexao = None
    try:
        conexao = criar_conexao()
        with conexao.cursor(dictionary=True) as cursor:
            if q:
                query = """
                    SELECT m.id, m.id_remetente, m.id_destinatario, m.post_id, m.mensagem, 
                           m.data_envio, m.lida, m.caminho_arquivo, m.id_mensagem_respondida,
                           ur.username AS remetente_username,
                           ud.username AS destinatario_username
                    FROM mensagens m
                    LEFT JOIN users ur ON m.id_remetente = ur.id
                    LEFT JOIN users ud ON m.id_destinatario = ud.id
                    WHERE 
                        m.id LIKE %s OR 
                        m.mensagem LIKE %s OR 
                        ur.username LIKE %s OR 
                        ud.username LIKE %s
                    ORDER BY m.data_envio DESC
                """
                cursor.execute(query, (f"%{q}%", f"%{q}%", f"%{q}%", f"%{q}%"))
            else:
                cursor.execute("""
                    SELECT m.id, m.id_remetente, m.id_destinatario, m.post_id, m.mensagem, 
                           m.data_envio, m.lida, m.caminho_arquivo, m.id_mensagem_respondida,
                           ur.username AS remetente_username,
                           ud.username AS destinatario_username
                    FROM mensagens m
                    LEFT JOIN users ur ON m.id_remetente = ur.id
                    LEFT JOIN users ud ON m.id_destinatario = ud.id
                    ORDER BY m.data_envio DESC
                """)
            mensagens = cursor.fetchall()
    except Exception as e:
        print("Erro ao buscar mensagens:", e)
        mensagens = []
    finally:
        if conexao:
            conexao.close()

    return render_template('sessao_mensagens_adm.html', mensagens=mensagens)
# =============================================================
#  PARA REMOVER AS MENSAGENS
# =============================================================
@administrador_bp.route('/excluir_mensagem/<int:id>', methods=['DELETE'])
def excluir_mensagem(id):
    if 'admin_id' not in session:
        return jsonify({'success': False, 'msg': 'Não autorizado'}), 401

    conexao = None
    try:
        conexao = criar_conexao()
        with conexao.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id_remetente FROM mensagens WHERE id = %s", (id,))
            mensagem = cursor.fetchone()

            if not mensagem:
                return jsonify({'success': False, 'msg': 'Mensagem não encontrada'}), 404

            usuario_id = mensagem['id_remetente']

            cursor.execute("SELECT email, username FROM users WHERE id = %s", (usuario_id,))
            user_info = cursor.fetchone()

            if user_info:
                enviar_email_remocao_mensagem(user_info['email'], user_info['username'])

            cursor.execute("DELETE FROM mensagens WHERE id = %s", (id,))
            conexao.commit()

            cursor.execute("""
                INSERT INTO notificacoes (usuario_id, tipo)
                VALUES (%s, 'mensagem_removida')
            """, (usuario_id,))
            conexao.commit()

        return jsonify({'success': True, 'msg': 'Mensagem excluída com sucesso!'})
    except Exception as e:
        print("Erro ao excluir mensagem:", e)
        return jsonify({'success': False, 'msg': 'Erro ao excluir mensagem.'}), 500
    finally:
        if conexao:
            conexao.close()
# =============================================================
#  PAGINA DE SESSAO DE PESQUISAS
# =============================================================
@administrador_bp.route('/sessao_pesquisas_adm')
def sessao_pesquisas_adm():
    if 'admin_id' not in session:
        return redirect(url_for('administrador.login_adm'))

    q = request.args.get('q', '').strip()
    conexao = None
    try:
        conexao = criar_conexao()
        with conexao.cursor(dictionary=True) as cursor:
            if q:
                query = """
                    SELECT p.id, p.usuario_id, p.termo, p.criado_em, u.username
                    FROM historico_pesquisa_post p
                    LEFT JOIN users u ON p.usuario_id = u.id
                    WHERE 
                        p.termo LIKE %s OR
                        u.username LIKE %s
                    ORDER BY p.criado_em DESC
                """
                cursor.execute(query, (f"%{q}%", f"%{q}%"))
            else:
                cursor.execute("""
                    SELECT p.id, p.usuario_id, p.termo, p.criado_em, u.username
                    FROM historico_pesquisa_post p
                    LEFT JOIN users u ON p.usuario_id = u.id
                    ORDER BY p.criado_em DESC
                """)
            pesquisas = cursor.fetchall()
    except Exception as e:
        print("Erro ao buscar pesquisas:", e)
        pesquisas = []
    finally:
        if conexao:
            conexao.close()

    return render_template('sessao_pesquisas_adm.html', pesquisas=pesquisas)
# =============================================================
#  PARA APAGAR AS PESQUISAS
# =============================================================
@administrador_bp.route('/apagar_pesquisa/<int:id>', methods=['DELETE'])
def apagar_pesquisa(id):
    if 'admin_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 403

    conexao = criar_conexao()
    try:
        with conexao.cursor() as cursor:
            cursor.execute("DELETE FROM historico_pesquisa_post WHERE id = %s", (id,))
            conexao.commit()
        return jsonify({'success': True}), 200
    except Exception as e:
        print("Erro ao apagar pesquisa:", e)
        return jsonify({'error': 'Erro no servidor'}), 500
    finally:
        conexao.close()