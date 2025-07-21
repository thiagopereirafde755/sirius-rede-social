from flask import Blueprint, redirect, url_for, session, jsonify
from app.conexao import criar_conexao

curtir_bp = Blueprint('curtir', __name__)

# =============================================================
#  PARA PODER CURTIR OU DESCURTIR POST
# =============================================================
@curtir_bp.route('/curtir/<int:post_id>', methods=['POST'])
def curtir(post_id):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()
        if not conexao:
            return jsonify(error="Erro na conexão com o banco de dados."), 500

        with conexao.cursor() as cursor:
            
            # VERIFICAR POST
            cursor.execute("SELECT users_id FROM posts WHERE id = %s", (post_id,))
            row = cursor.fetchone()
            if not row:
                return jsonify(error="Post não encontrado"), 404
            dono_post_id = row[0]

            # VERIFICA SE JA CURTIU
            cursor.execute("""
                SELECT 1 FROM curtidas
                WHERE post_id = %s AND usuario_id = %s
            """, (post_id, usuario_id))
            ja_curtiu = cursor.fetchone() is not None

            if not ja_curtiu:
                # CURTIR
                cursor.execute("""
                    INSERT INTO curtidas (post_id, usuario_id, data)
                    VALUES (%s, %s, NOW())
                """, (post_id, usuario_id))

                # NOTIFICA SE NAO FOR O PROPRIO POST
                if dono_post_id != usuario_id:
                    cursor.execute("""
                        INSERT INTO notificacoes
                        (usuario_id, tipo, origem_usuario_id, post_id, lida)
                        VALUES (%s, 'curtida', %s, %s, 0)
                    """, (dono_post_id, usuario_id, post_id))

                curtido = True
            else:
                # DESCURTIR
                cursor.execute("""
                    DELETE FROM curtidas
                    WHERE post_id = %s AND usuario_id = %s
                """, (post_id, usuario_id))

                # APAGAR A NOTIFICAÇÃO DAQUELA CURTIDA
                if dono_post_id != usuario_id:
                    cursor.execute("""
                        DELETE FROM notificacoes
                        WHERE usuario_id = %s
                          AND origem_usuario_id = %s
                          AND post_id = %s
                          AND tipo = 'curtida'
                    """, (dono_post_id, usuario_id, post_id))

                curtido = False

            # CONTAGEM DE CURTIDAS
            cursor.execute("SELECT COUNT(*) FROM curtidas WHERE post_id = %s", (post_id,))
            curtidas_count = cursor.fetchone()[0]

        conexao.commit()
        return jsonify(curtidas=curtidas_count, curtido=curtido)

    except Exception as e:
        return jsonify(error=f"Erro no servidor: {e}"), 500
    finally:
        if conexao: conexao.close()
# =============================================================
#  BUSCAR USUARIOS QUE CURTIU POST
# =============================================================
@curtir_bp.route('/curtidas/<int:post_id>/usuarios', methods=['GET'])
def usuarios_que_curtiram(post_id):
    try:
        conexao = criar_conexao()
        with conexao.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT u.id, u.username, u.fotos_perfil
                FROM curtidas c
                JOIN users u ON c.usuario_id = u.id
                WHERE c.post_id = %s
            """, (post_id,))
            usuarios = cursor.fetchall()
        conexao.close()
        return jsonify({'usuarios': usuarios})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    



