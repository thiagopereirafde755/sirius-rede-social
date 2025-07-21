from flask import Blueprint, session, jsonify
from app.conexao import criar_conexao

apagar_comentario_bp = Blueprint('apagarcommen', __name__)

# =============================================================
#  PARA APAGAR O COMENTARIO
# =============================================================
@apagar_comentario_bp.route('/apagar_comentario/<int:comentario_id>', methods=['POST'])
def apagar_comentario(comentario_id):
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'Você precisa estar logado para apagar comentários.'})

    conexao = criar_conexao()
    cursor = conexao.cursor()

    try:
        
        # PEGAR O ID DO POST E DO DONO
        cursor.execute("SELECT post_id, usuario_id FROM comentarios WHERE id = %s", (comentario_id,))
        resultado = cursor.fetchone()

        if not resultado:
            return jsonify({'success': False, 'message': 'Comentário não encontrado.'})

        post_id = resultado[0]
        comentario_usuario_id = resultado[1]

        # VERIFICA SE O USER E DONO DO POST
        cursor.execute("SELECT users_id FROM posts WHERE id = %s", (post_id,))
        post_resultado = cursor.fetchone()

        if comentario_usuario_id == session['usuario_id'] or (post_resultado and post_resultado[0] == session['usuario_id']):

            # PRIMEIRO APAGA AS RESPOSTA
            def apagar_respostas(parent_id):
                cursor.execute("SELECT id FROM comentarios WHERE parent_comment_id = %s", (parent_id,))
                respostas = cursor.fetchall()
                for resposta in respostas:
                    apagar_respostas(resposta[0])
                    cursor.execute("DELETE FROM comentarios WHERE id = %s", (resposta[0],))

            apagar_respostas(comentario_id)
            cursor.execute("DELETE FROM comentarios WHERE id = %s", (comentario_id,))
            cursor.execute("SELECT COUNT(*) FROM comentarios WHERE post_id = %s", (post_id,))
            total_comentarios = cursor.fetchone()[0]

            conexao.commit()
            return jsonify({
                'success': True, 
                'message': 'Comentário apagado com sucesso.',
                'comentarios_count': total_comentarios,
                'post_id': post_id
            })
        else:
            return jsonify({'success': False, 'message': 'Você não tem permissão para apagar este comentário.'})
    except Exception as e:
        conexao.rollback()
        return jsonify({'success': False, 'message': f'Erro ao apagar comentário: {str(e)}'})
    finally:
        cursor.close()
        conexao.close()
