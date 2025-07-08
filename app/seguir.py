import os
from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
from werkzeug.utils import secure_filename
from app.utils import formatar_data
from app.conexao import criar_conexao
from datetime import datetime

seguir_bp = Blueprint('seguir_user', __name__)

@seguir_bp.route('/seguir/<int:id_usuario>', methods=['POST'])
def seguir(id_usuario):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))  # Redireciona se não estiver logado

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()
        
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Verifica se o usuário já segue o outro usuário
                cursor.execute("""
                    SELECT * FROM seguindo WHERE id_seguidor = %s AND id_seguindo = %s
                """, (usuario_id, id_usuario))
                seguir_existente = cursor.fetchone()

                if seguir_existente:
                    # Se já segue, deixar de seguir
                    cursor.execute("""
                        DELETE FROM seguindo WHERE id_seguidor = %s AND id_seguindo = %s
                    """, (usuario_id, id_usuario))
                    conexao.commit()
                    flash("Você deixou de seguir este usuário.", "info")
                else:
                    # Caso contrário, seguir
                    cursor.execute("""
                        INSERT INTO seguindo (id_seguidor, id_seguindo) VALUES (%s, %s)
                    """, (usuario_id, id_usuario))
                    conexao.commit()
                    flash("Você começou a seguir este usuário.", "success")

                    # Inserir notificação de seguidor
                    cursor.execute("""
                        INSERT INTO notificacoes (usuario_id, tipo, origem_usuario_id, post_id, lida)
                        VALUES (%s, 'seguidor', %s, NULL, 0)
                    """, (id_usuario, usuario_id))  # id_usuario é quem recebe a notificação
                    conexao.commit()

            conexao.close()

            # Redireciona de volta para a página do perfil
            return redirect(url_for('info_user.info_user', id_usuario=id_usuario))
        
        return "Erro na conexão com o banco de dados."

    except Exception as e:
        return f"Erro ao conectar ao banco de dados: {str(e)}"

@seguir_bp.route('/pedir-para-seguir/<int:id_usuario>', methods=['POST'])
def pedir_para_seguir(id_usuario):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
                # Verifica se já existe um pedido pendente
                cursor.execute("""
                    SELECT * FROM pedidos_seguir WHERE id_solicitante = %s AND id_destino = %s
                """, (usuario_id, id_usuario))
                pedido = cursor.fetchone()

                if not pedido:
                    # Inserir pedido
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

                # Remove notificação do pedido também
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
    
@seguir_bp.route('/aceitar-pedido/<int:id_pedido>/<int:id_usuario>', methods=['POST'])
def aceitar_pedido(id_pedido, id_usuario):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']  # usuario_id é quem está ACEITANDO

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
            # Aceitar o pedido: adiciona à tabela seguindo
                cursor.execute("""
                    INSERT INTO seguindo (id_seguidor, id_seguindo) VALUES (%s, %s)
                """, (id_usuario, usuario_id))

                # Remove o pedido da tabela
                cursor.execute("DELETE FROM pedidos_seguir WHERE id = %s", (id_pedido,))

                # Notifica o solicitante que você aceitou o pedido dele (tipo novo: 'aceite_pedido')
                cursor.execute("""
                    INSERT INTO notificacoes (usuario_id, tipo, origem_usuario_id, post_id, lida)
                    VALUES (%s, 'aceite_pedido', %s, NULL, 0)
                """, (id_usuario, usuario_id))
                # id_usuario = solicitante, usuario_id = quem aceitou

            conexao.commit()

            conexao.close()
            flash("Você aceitou o pedido de seguir.", "success")
        return redirect(url_for('notificacao.notificacoes'))

    except Exception as e:
        return f"Erro ao aceitar pedido: {str(e)}"

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
            with conexao.cursor(dictionary=True) as cursor:  # Note o dictionary=True aqui
                if seguir:
                    # Verificar se já não está seguindo
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
                
                # Obter contagem atualizada de seguidores
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
                # Conta seguidores atualizados
                cursor.execute("SELECT COUNT(*) FROM seguindo WHERE id_seguindo = %s", (usuario_id,))
                seguidores_count = cursor.fetchone()[0]
            conexao.close()
            return jsonify({'success': True, 'seguidores_count': seguidores_count})
        else:
            return jsonify({'success': False, 'error': 'Erro ao conectar ao banco de dados.'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 

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
                # Conta seguindo atualizados
                cursor.execute("SELECT COUNT(*) FROM seguindo WHERE id_seguidor = %s", (usuario_id,))
                seguindo_count = cursor.fetchone()[0]
            conexao.close()
            return jsonify({'success': True, 'seguindo_count': seguindo_count})
        else:
            return jsonify({'success': False, 'error': 'Erro ao conectar ao banco de dados.'}), 500
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

