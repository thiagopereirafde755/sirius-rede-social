from flask import Blueprint, render_template, redirect, url_for, session, request
from app.conexao import criar_conexao
from app.utils import buscar_hashtags_mais_usadas, buscar_info_usuario_logado_1

prucura_user_bp = Blueprint('procurar_user', __name__)

# =============================================================
#  PAGINA PARA PODER PESQUISAR USUARIOS
# =============================================================
@prucura_user_bp.route('/procurar-user')
def inicio():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']
    query = request.args.get('query', '')

    try:
        conexao = criar_conexao()

        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # INFORMAÇÃO DO USUARIO LOGADO
                foto_perfil, nome_usuario, tema = buscar_info_usuario_logado_1(cursor, usuario_id)

                # HASHTAG DO MOMENTO
                hashtags_top = buscar_hashtags_mais_usadas(cursor)

                if query:
                    cursor.execute("SELECT id, username, fotos_perfil FROM users WHERE username LIKE %s", (f"%{query}%",))
                    resultados = cursor.fetchall()
                    historico = []
                else:
                    cursor.execute("""
                        SELECT u.id, u.username, u.fotos_perfil
                        FROM historico_pesquisa_procurar_usuarios h
                        JOIN users u ON u.id = h.usuario_pesquisado_id
                        WHERE h.usuario_id = %s
                        ORDER BY h.data_pesquisa DESC
                        LIMIT 10
                    """, (usuario_id,))
                    historico = cursor.fetchall()
                    resultados = []

                conexao.close()

            return render_template('procurar-user.html',
                usuario_id=usuario_id,
                foto_perfil=foto_perfil,
                nome_usuario=nome_usuario,
                tema=tema,
                query=query,
                resultados=resultados,
                historico=historico,
                hashtags_top=hashtags_top
            )

        return "Erro na conexão com o banco de dados."
    except Exception as e:
        return f"Erro ao conectar ao banco de dados: {str(e)}"
# =============================================================
#  REMOVER HISTORICO DE PESQUISA
# =============================================================    
@prucura_user_bp.route('/remover-historico', methods=['POST'])
def remover_historico():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']
    id_pesquisado = request.form.get('id_pesquisado')

    try:
        conexao = criar_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                DELETE FROM historico_pesquisa_procurar_usuarios
                WHERE usuario_id = %s AND usuario_pesquisado_id = %s
            """, (usuario_id, id_pesquisado))
        conexao.commit()
        conexao.close()
    except Exception as e:
        print("Erro ao remover do histórico:", e)

    return redirect(url_for('procurar_user.inicio'))
# =============================================================
#  SALVAR HISTORICO DE PESQUISA
# ============================================================= 
@prucura_user_bp.route('/salvar-historico', methods=['POST'])
def salvar_historico_ajax():
    if 'usuario_id' not in session:
        return 'Não autorizado', 401

    data = request.get_json()
    usuario_id = session['usuario_id']
    pesquisado_id = data.get('id_pesquisado')

    try:
        conexao = criar_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                INSERT INTO historico_pesquisa_procurar_usuarios (usuario_id, usuario_pesquisado_id)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE data_pesquisa = CURRENT_TIMESTAMP
            """, (usuario_id, pesquisado_id))
        conexao.commit()
        return 'OK', 200
    except Exception as e:
        print("Erro ao salvar histórico AJAX:", e)
        return 'Erro', 500
    finally:
        if conexao: conexao.close()


