from flask import Blueprint, redirect, url_for, session, request, flash, jsonify
from app.conexao import criar_conexao

seguir_bp = Blueprint('seguir_user', __name__)

# =============================================================
#  PARA SEGUIR USER
# =============================================================
@seguir_bp.route('/seguir/<int:id_usuario>', methods=['POST'])
def seguir(id_usuario):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))  

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()
        
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:

                # VERIFICA SE JA SEGUI
                cursor.execute("""
                    SELECT * FROM seguindo WHERE id_seguidor = %s AND id_seguindo = %s
                """, (usuario_id, id_usuario))
                seguir_existente = cursor.fetchone()

                if seguir_existente:

                    # SE JA SEGUE DEIXA DE SEGUIR
                    cursor.execute("""
                        DELETE FROM seguindo WHERE id_seguidor = %s AND id_seguindo = %s
                    """, (usuario_id, id_usuario))
                    conexao.commit()
                    flash("Você deixou de seguir este usuário.", "info")
                else:
                    # CASO NAO ELE SEGUI
                    cursor.execute("""
                        INSERT INTO seguindo (id_seguidor, id_seguindo) VALUES (%s, %s)
                    """, (usuario_id, id_usuario))
                    conexao.commit()
                    flash("Você começou a seguir este usuário.", "success")

                    # E NOTIFICA
                    cursor.execute("""
                        INSERT INTO notificacoes (usuario_id, tipo, origem_usuario_id, post_id, lida)
                        VALUES (%s, 'seguidor', %s, NULL, 0)
                    """, (id_usuario, usuario_id))  
                    conexao.commit()

            conexao.close()

            return redirect(url_for('info_user.info_user', id_usuario=id_usuario))
        
        return "Erro na conexão com o banco de dados."

    except Exception as e:
        return f"Erro ao conectar ao banco de dados: {str(e)}"
# =============================================================
#  PEDIR PARA SEGUIR
# =============================================================
@seguir_bp.route('/pedir-para-seguir/<int:id_usuario>', methods=['POST'])
def pedir_para_seguir(id_usuario):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:

                # VERIFICA SE JA EXISTE PEDIDO
                cursor.execute("""
                    SELECT * FROM pedidos_seguir WHERE id_solicitante = %s AND id_destino = %s
                """, (usuario_id, id_usuario))
                pedido = cursor.fetchone()

                if not pedido:

                    # INSERIR O PEDIDO
                    cursor.execute("""
                        INSERT INTO pedidos_seguir (id_solicitante, id_destino)
                        VALUES (%s, %s)
                    """, (usuario_id, id_usuario))
                    conexao.commit()

                    flash("Pedido de seguir enviado.", "info")
            conexao.close()
        return redirect(url_for('info_user.info_user', id_usuario=id_usuario))
    except Exception as e:
        return f"Erro ao processar pedido de seguir: {str(e)}"
# =============================================================
#  CANCELAR PEDIDO
# =============================================================
@seguir_bp.route('/cancelar-pedido/<int:id_usuario>', methods=['POST'])
def cancelar_pedido(id_usuario):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']
    
    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM pedidos_seguir
                    WHERE id_solicitante = %s AND id_destino = %s
                """, (usuario_id, id_usuario))
                conexao.commit()

                # REMOVE O PEDIDO
                cursor.execute("""
                    DELETE FROM notificacoes
                    WHERE usuario_id = %s AND origem_usuario_id = %s AND tipo = 'pedido_seguir' AND post_id IS NULL
                """, (id_usuario, usuario_id))
                conexao.commit()

                flash("Pedido de seguir cancelado.", "info")
            conexao.close()
        return redirect(url_for('info_user.info_user', id_usuario=id_usuario))
    except Exception as e:
        return f"Erro ao cancelar pedido: {str(e)}"
# =============================================================
#  ACEITAR PEDIDO
# =============================================================
@seguir_bp.route('/aceitar-pedido/<int:id_pedido>/<int:id_usuario>', methods=['POST'])
def aceitar_pedido(id_pedido, id_usuario):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id'] 

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:

                # SALVA COMO SEGUIDO
                cursor.execute("""
                    INSERT INTO seguindo (id_seguidor, id_seguindo) VALUES (%s, %s)
                """, (id_usuario, usuario_id))

                # REMOVE O PEDIDO
                cursor.execute("DELETE FROM pedidos_seguir WHERE id = %s", (id_pedido,))

                # NOTIFICA QUE O PEDIDO FOI ACEITO
                cursor.execute("""
                    INSERT INTO notificacoes (usuario_id, tipo, origem_usuario_id, post_id, lida)
                    VALUES (%s, 'aceite_pedido', %s, NULL, 0)
                """, (id_usuario, usuario_id))

            conexao.commit()

            conexao.close()
            flash("Você aceitou o pedido de seguir.", "success")
        return redirect(url_for('notificacao.notificacoes'))

    except Exception as e:
        return f"Erro ao aceitar pedido: {str(e)}"
# =============================================================
#  RECUSAR PEDIDO
# =============================================================
@seguir_bp.route('/recusar-pedido/<int:id_pedido>', methods=['POST'])
def recusar_pedido(id_pedido):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
                cursor.execute("DELETE FROM pedidos_seguir WHERE id = %s", (id_pedido,))
                conexao.commit()
            conexao.close()
            flash("Você recusou o pedido de seguir.", "info")
        return redirect(url_for('notificacao.notificacoes'))

    except Exception as e:
        return f"Erro ao recusar pedido: {str(e)}"
# =============================================================
#  SEGUIR PELO POST
# =============================================================
@seguir_bp.route('/toggle_seguir', methods=['POST'])
def toggle_seguir():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'})

    usuario_id = session['usuario_id']
    user_id = request.form.get('user_id')
    seguir = request.form.get('seguir') == 'true'

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:  
                if seguir:

                    # VERIFICA SE JA ESTA SEGUINDO
                    cursor.execute("""
                        SELECT * FROM seguindo 
                        WHERE id_seguidor = %s AND id_seguindo = %s
                    """, (usuario_id, user_id))
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO seguindo (id_seguidor, id_seguindo, data_seguindo)
                            VALUES (%s, %s, NOW())
                        """, (usuario_id, user_id))
                else:
                    cursor.execute("""
                        DELETE FROM seguindo 
                        WHERE id_seguidor = %s AND id_seguindo = %s
                    """, (usuario_id, user_id))
                
                # OBTER O NUMERO DE SEGUIDORES
                cursor.execute("""
                    SELECT COUNT(*) as seguidores_count 
                    FROM seguindo 
                    WHERE id_seguindo = %s
                """, (user_id,))
                result = cursor.fetchone()
                seguidores_count = result['seguidores_count'] if result else 0
                
                conexao.commit()
                return jsonify({
                    'success': True,
                    'seguidores_count': seguidores_count
                })
        
        return jsonify({'success': False, 'message': 'Erro na conexão com o banco de dados'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})
# =============================================================
#  REMOVER SEGUIDOR PELO MODAL
# =============================================================
@seguir_bp.route('/remover_seguidor', methods=['POST'])
def remover_seguidor():
    if 'usuario_id' not in session:
        return jsonify({'success': False}), 401
    usuario_id = session['usuario_id']
    seguidor_id = request.form.get('seguidor_id')
    if not seguidor_id:
        return jsonify({'success': False, 'error': 'ID do seguidor não informado.'}), 400

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM seguindo WHERE id_seguidor = %s AND id_seguindo = %s
                """, (seguidor_id, usuario_id))
                conexao.commit()
                # CONTA ATUALIZADA
                cursor.execute("SELECT COUNT(*) FROM seguindo WHERE id_seguindo = %s", (usuario_id,))
                seguidores_count = cursor.fetchone()[0]
            conexao.close()
            return jsonify({'success': True, 'seguidores_count': seguidores_count})
        else:
            return jsonify({'success': False, 'error': 'Erro ao conectar ao banco de dados.'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 
# =============================================================
#  DEIXAR DE SEGUIR PELO MODAL
# =============================================================
@seguir_bp.route('/deixar_de_seguir', methods=['POST'])
def deixar_de_seguir():
    if 'usuario_id' not in session:
        return jsonify({'success': False}), 401
    usuario_id = session['usuario_id']
    seguindo_id = request.form.get('seguindo_id')
    if not seguindo_id:
        return jsonify({'success': False, 'error': 'ID do seguindo não informado.'}), 400

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM seguindo WHERE id_seguidor = %s AND id_seguindo = %s
                """, (usuario_id, seguindo_id))
                conexao.commit()
                # CONTA ATUALIZADA
                cursor.execute("SELECT COUNT(*) FROM seguindo WHERE id_seguidor = %s", (usuario_id,))
                seguindo_count = cursor.fetchone()[0]
            conexao.close()
            return jsonify({'success': True, 'seguindo_count': seguindo_count})
        else:
            return jsonify({'success': False, 'error': 'Erro ao conectar ao banco de dados.'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

