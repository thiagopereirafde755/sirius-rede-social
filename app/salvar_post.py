from flask import Blueprint, redirect, url_for, session, jsonify
from app.conexao import criar_conexao
from mysql.connector.errors import IntegrityError

salvar_bp = Blueprint('salvar', __name__)

# =============================================================
#  SALVAR OU DESFAZER SALVAMENTO DE POST
# =============================================================
@salvar_bp.route('/salvar/<int:post_id>', methods=['POST'])
def salvar_post(post_id):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']
    conexao    = None

    try:
        conexao = criar_conexao()
        if not conexao:
            return jsonify(error='Erro na conexão com o banco de dados.'), 500

        with conexao.cursor(dictionary=True) as cur:
            
            # VERIFICA SE O POST EXISTE
            cur.execute("SELECT users_id FROM posts WHERE id = %s", (post_id,))
            post = cur.fetchone()
            if not post:
                return jsonify(error='Post não encontrado'), 404

            # VERIFICA SE JA SALVOU
            cur.execute("""
               SELECT 1
                 FROM posts_salvos
                WHERE post_id = %s AND usuario_id = %s
            """, (post_id, usuario_id))
            ja_salvou = cur.fetchone() is not None

            if ja_salvou:
                cur.execute("""
                    DELETE FROM posts_salvos
                     WHERE post_id = %s AND usuario_id = %s
                """, (post_id, usuario_id))
                salvado = False
            else:
                try:
                    cur.execute("""
                        INSERT INTO posts_salvos
                            (post_id, usuario_id, data)
                        VALUES (%s, %s, NOW())
                    """, (post_id, usuario_id))
                    salvado = True
                except IntegrityError:
                    salvado = True

            # CONTA O SALVOS
            cur.execute("""
                SELECT COUNT(*) AS total
                  FROM posts_salvos
                 WHERE post_id = %s
            """, (post_id,))
            salvados = cur.fetchone()['total']

        conexao.commit()
        return jsonify(salvados=salvados, salvado=salvado)

    except Exception as e:
        print('[ROTA /salvar] Erro:', e)
        return jsonify(error=f'Erro no servidor: {e}'), 500

    finally:
        if conexao:
            conexao.close()