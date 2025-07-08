from flask import Blueprint, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
from app.conexao import criar_conexao

curtir_bp = Blueprint('curtir', __name__)

@curtir_bp.route('/curtir/<int:post_id>', methods=['POST'])
def curtir(post_id):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()

        if conexao:
            with conexao.cursor() as cursor:
                # Verifica se o usuário já curtiu o post
                cursor.execute("""
                    SELECT * FROM curtidas 
                    WHERE post_id = %s AND usuario_id = %s
                """, (post_id, usuario_id))
                curtida = cursor.fetchone()

                if not curtida:
                    # Se não tiver curtido, adiciona a curtida COM DATA
                    cursor.execute("""
                        INSERT INTO curtidas (post_id, usuario_id, data) 
                        VALUES (%s, %s, NOW())
                    """, (post_id, usuario_id))
                    curtido = True  # Indica que o usuário curtiu o post

                    # Busca o dono do post
                    cursor.execute("""
                        SELECT users_id FROM posts WHERE id = %s
                    """, (post_id,))
                    resultado = cursor.fetchone()
                    if resultado:
                        dono_post_id = resultado[0]
                        if dono_post_id != usuario_id:  # Não notifica o próprio usuário
                            # Registra notificação
                            cursor.execute("""
                                INSERT INTO notificacoes 
                                (usuario_id, tipo, origem_usuario_id, post_id, lida) 
                                VALUES (%s, 'curtida', %s, %s, 0)
                            """, (dono_post_id, usuario_id, post_id))
                else:
                    # Se já tiver curtido, remove a curtida
                    cursor.execute("""
                        DELETE FROM curtidas 
                        WHERE post_id = %s AND usuario_id = %s
                    """, (post_id, usuario_id))
                    curtido = False  # Indica que o usuário descurtiu o post

                # Recuperar a nova contagem de curtidas
                cursor.execute("""
                    SELECT COUNT(*) FROM curtidas WHERE post_id = %s
                """, (post_id,))
                curtidas_count = cursor.fetchone()[0]

                conexao.commit()
                conexao.close()

                # Retorna a contagem de curtidas e o estado de curtida
                return jsonify(curtidas=curtidas_count, curtido=curtido)

        return jsonify(error="Erro na conexão com o banco de dados."), 500

    except Exception as e:
        return jsonify(error=f"Erro ao conectar ao banco de dados: {str(e)}"), 500
        
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
    



