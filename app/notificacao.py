from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from app.conexao import criar_conexao
from app.utils import buscar_hashtags_mais_usadas, buscar_info_usuario_logado_1

notificacao_bp = Blueprint('notificacao', __name__)

@notificacao_bp.route('/notificacoes')
def notificacoes():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # <-- ADICIONE ISSO ANTES DE BUSCAR AS NOTIFICAÇÕES -->
                # cursor.execute("""
                #     UPDATE notificacoes
                #     SET lida = 1
                #     WHERE usuario_id = %s AND lida = 0
                # """, (usuario_id,))
                # conexao.commit()
                # -----------------------------------------------

                # INFORMACOES DO USUARIO LOGADO
                foto_perfil, nome_usuario, tema = buscar_info_usuario_logado_1(cursor, usuario_id)

                # HASHTAG DO MOMENTO
                hashtags_top = buscar_hashtags_mais_usadas(cursor)

                # Buscar pedidos de seguir pendentes
                cursor.execute("""
                    SELECT ps.id, u.id as id_usuario, u.username, u.fotos_perfil, ps.data_pedido
                    FROM pedidos_seguir ps
                    JOIN users u ON ps.id_solicitante = u.id
                    WHERE ps.id_destino = %s
                """, (usuario_id,))
                pedidos = cursor.fetchall()
                for pedido in pedidos:
                    pedido['tipo'] = 'pedido_seguir'
                    pedido['origem_username'] = pedido['username']
                    pedido['origem_foto'] = pedido['fotos_perfil']
                    pedido['data_evento'] = pedido['data_pedido']
                    pedido['origem_usuario_id'] = pedido['id_usuario']

                # Buscar notificações do usuário
                cursor.execute("""
    SELECT n.id, n.tipo, n.data_notificacao, n.lida, n.post_id, n.comentario_id,
           n.origem_usuario_id,
           u.username as origem_username, u.fotos_perfil as origem_foto
    FROM notificacoes n
    JOIN users u ON n.origem_usuario_id = u.id
    WHERE n.usuario_id = %s
      AND n.data_notificacao >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    ORDER BY n.data_notificacao DESC
    LIMIT 30
""", (usuario_id,))
                notificacoes = cursor.fetchall()
                for n in notificacoes:
                    n['data_evento'] = n['data_notificacao']

                itens = pedidos + notificacoes
                itens.sort(key=lambda x: x['data_evento'], reverse=True)

            conexao.close()
            return render_template(
                'notificacoes.html',
                itens=itens,
                usuario_id=usuario_id,
                foto_perfil=foto_perfil,
                nome_usuario=nome_usuario,
                hashtags_top=hashtags_top,
                username=nome_usuario,
                tema=tema
            )
        return "Erro na conexão com o banco de dados."
    except Exception as e:
        return f"Erro ao buscar notificações: {str(e)}"
    
@notificacao_bp.route('/api/notificacoes_nao_lidas', methods=['GET'])
def contar_notificacoes_nao_lidas():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'error': 'Usuário não autenticado'})
    usuario_id = session['usuario_id']
    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT COUNT(*) AS nao_lidas
                    FROM notificacoes
                    WHERE usuario_id = %s AND lida = 0
                """, (usuario_id,))
                resultado = cursor.fetchone()
            conexao.close()
            return jsonify({'success': True, 'nao_lidas': resultado['nao_lidas'] or 0})
        return jsonify({'success': False, 'error': 'Erro na conexão com o banco de dados.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@notificacao_bp.route('/api/notificacoes_ultimas', methods=['GET'])
def ultimas_notificacoes():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'error': 'Usuário não autenticado'})
    usuario_id = session['usuario_id']
    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT n.id, n.tipo, n.data_notificacao, n.lida, n.post_id, n.comentario_id,
                        n.origem_usuario_id,
                        u.username as origem_username, u.fotos_perfil as origem_foto
                    FROM notificacoes n
                    JOIN users u ON n.origem_usuario_id = u.id
                    WHERE n.usuario_id = %s
                        AND n.lida = 0
                    ORDER BY n.data_notificacao DESC
                    LIMIT 1
                """, (usuario_id,))
                notificacao = cursor.fetchone()
            conexao.close()
            return jsonify({'success': True, 'notificacao': notificacao})
        return jsonify({'success': False, 'error': 'Erro na conexão com o banco de dados.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@notificacao_bp.route('/api/marcar_como_lidas', methods=['POST'])
def marcar_como_lidas():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'error': 'Usuário não autenticado'})
    
    usuario_id = session['usuario_id']
    
    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
                cursor.execute("""
                    UPDATE notificacoes
                    SET lida = 1
                    WHERE usuario_id = %s AND lida = 0
                """, (usuario_id,))
                conexao.commit()
            conexao.close()
            return jsonify({'success': True})
        return jsonify({'success': False, 'error': 'Erro na conexão com o banco de dados.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})