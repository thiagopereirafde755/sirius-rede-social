from flask import Blueprint, redirect, url_for, session, jsonify
from app.conexao import criar_conexao

republicar_bp = Blueprint('republicar', __name__)

# =============================================================
#  REPUBLICAR OU DESFAZER REPUBLICAÇÃO
# =============================================================
@republicar_bp.route('/republicar/<int:post_id>', methods=['POST'])
def republicar(post_id):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']
    conexao = None

    try:
        conexao = criar_conexao()
        if not conexao:
            return jsonify(error='Erro na conexão com o banco de dados.'), 500

        with conexao.cursor(dictionary=True) as cur:

            # VERIFICA SE O POST EXISTE E PEGA O DONO
            cur.execute("SELECT users_id FROM posts WHERE id = %s", (post_id,))
            post = cur.fetchone()
            if not post:
                return jsonify(error='Post não encontrado'), 404
            dono_post_id = post['users_id']

            # VERIFICA SE JÁ REPUBLICOU
            cur.execute("""
                SELECT 1
                  FROM posts_republicados
                 WHERE post_id = %s AND usuario_id = %s
            """, (post_id, usuario_id))
            ja_republicou = cur.fetchone() is not None

            if ja_republicou:
                # REMOVER REPUBLICAÇÃO
                cur.execute("""
                    DELETE FROM posts_republicados
                     WHERE post_id = %s AND usuario_id = %s
                """, (post_id, usuario_id))

                # REMOVER NOTIFICAÇÃO DE REPUBLICAÇÃO (se não for o próprio dono)
                if dono_post_id != usuario_id:
                    cur.execute("""
                        DELETE FROM notificacoes
                        WHERE usuario_id = %s
                          AND origem_usuario_id = %s
                          AND post_id = %s
                          AND tipo = 'republicado'
                    """, (dono_post_id, usuario_id, post_id))

                republicado = False

            else:
                # INSERIR REPUBLICAÇÃO
                cur.execute("""
                    INSERT INTO posts_republicados
                        (post_id, usuario_id, data)
                    VALUES (%s, %s, NOW())
                """, (post_id, usuario_id))

                # INSERIR NOTIFICAÇÃO DE REPUBLICAÇÃO (se não for o próprio dono)
                if dono_post_id != usuario_id:
                    cur.execute("""
                        INSERT INTO notificacoes
                            (usuario_id, tipo, origem_usuario_id, post_id, lida)
                        VALUES (%s, 'republicado', %s, %s, 0)
                    """, (dono_post_id, usuario_id, post_id))

                republicado = True

            # CONTAR REPUBLICAÇÕES
            cur.execute("""
                SELECT COUNT(*) AS total
                  FROM posts_republicados
                 WHERE post_id = %s
            """, (post_id,))
            republicados = cur.fetchone()['total']

        conexao.commit()
        return jsonify(republicados=republicados, republicado=republicado)

    except Exception as e:
        print('[ROTA /republicar] Erro:', e)
        return jsonify(error=f'Erro no servidor: {e}'), 500

    finally:
        if conexao:
            conexao.close()
# =============================================================
#  LISTAR USUÁRIOS QUE REPUBLICARAM UM POST
# =============================================================
@republicar_bp.route('/republicados/<int:post_id>/usuarios')
def republicados_usuarios(post_id):
    if 'usuario_id' not in session:
        return jsonify({'error': 'Não autorizado'}), 403

    usuario_id = session['usuario_id']
    conexao = None

    try:
        conexao = criar_conexao()
        if not conexao:
            return jsonify({'error': 'Erro ao conectar com o banco de dados'}), 500

        with conexao.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT u.id, u.username, u.fotos_perfil
                FROM posts_republicados pr
                JOIN users u ON pr.usuario_id = u.id
                WHERE pr.post_id = %s
            """, (post_id,))
            usuarios = cursor.fetchall()

        for user in usuarios:
            if not user['fotos_perfil']:
                user['fotos_perfil'] = url_for('static', filename='img/icone/user.png')

        return jsonify({'usuarios': usuarios, 'usuario_logado': usuario_id})

    except Exception as e:
        print('[ROTA /republicados/<id>/usuarios] Erro:', e)
        return jsonify({'error': str(e)}), 500

    finally:
        if conexao:
            conexao.close()