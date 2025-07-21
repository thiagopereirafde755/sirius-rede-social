from flask import Blueprint, url_for, session, request, jsonify
from app.conexao import criar_conexao

mencao_comentario_post_bp = Blueprint('mencao_comentario_post', __name__)

# =============================================================
#  BUSCA OS USUARIOS
# =============================================================
@mencao_comentario_post_bp.route('/buscar_usuarios')
def buscar_usuarios():
    if 'usuario_id' not in session:
        return jsonify([])

    search_term = request.args.get('q', '').lower()
    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                
                # PARA SABER SE O USER LOGADO E PRIVADO
                cursor.execute("SELECT perfil_publico FROM users WHERE id = %s", (usuario_id,))
                me_privado = cursor.fetchone()
                me_privado = me_privado and me_privado['perfil_publico'] == 0

                params = []
                if me_privado:

                    # SO APARECE QUE ME SEGUI
                    query = """
                        SELECT u.id, u.username, u.fotos_perfil
                        FROM users u
                        INNER JOIN seguindo s ON u.id = s.id_seguindo AND s.id_seguidor = %s
                        WHERE u.id != %s
                        AND LOWER(u.username) LIKE %s
                        AND NOT EXISTS (
                            SELECT 1 FROM bloqueados b
                            WHERE (b.usuario_id = u.id AND b.bloqueado_id = %s)
                               OR (b.usuario_id = %s AND b.bloqueado_id = u.id)
                        )
                        LIMIT 5
                    """
                    params = [usuario_id, usuario_id, f"%{search_term}%", usuario_id, usuario_id]
                else:

                    # SE O OUTRO USER E PRIVADO SO QUE EU SIGO
                    query = """
                        SELECT u.id, u.username, u.fotos_perfil
                        FROM users u
                        WHERE u.id != %s
                        AND LOWER(u.username) LIKE %s
                        AND (
                            u.perfil_publico = 1
                            OR EXISTS (
                                SELECT 1 FROM seguindo s2 WHERE s2.id_seguindo = u.id AND s2.id_seguidor = %s
                            )
                        )
                        AND NOT EXISTS (
                            SELECT 1 FROM bloqueados b
                            WHERE (b.usuario_id = u.id AND b.bloqueado_id = %s)
                               OR (b.usuario_id = %s AND b.bloqueado_id = u.id)
                        )
                        LIMIT 5
                    """
                    params = [usuario_id, f"%{search_term}%", usuario_id, usuario_id, usuario_id]

                cursor.execute(query, tuple(params))
                users = cursor.fetchall()

                for user in users:
                    if not user['fotos_perfil']:
                        user['fotos_perfil'] = url_for('static', filename='img/icone/user.png')
                return jsonify(users)
    except Exception as e:
        print(f"Erro ao buscar usuários: {e}")

    return jsonify([])