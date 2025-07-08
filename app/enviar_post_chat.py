import os
from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from werkzeug.utils import secure_filename
from app.conexao import criar_conexao
from flask import jsonify
from datetime import datetime

enviar_post_chat_bp = Blueprint('eviarpostchat', __name__)

@enviar_post_chat_bp.route('/get_usuarios_mutuos')
def get_usuarios_mutuos():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'})

    usuario_id = session['usuario_id']
    post_id = request.args.get('post_id')

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Busca usuários que o usuário atual segue E que também seguem o usuário atual
                cursor.execute("""
                    SELECT u.id, u.username, u.fotos_perfil
                    FROM users u
                    JOIN seguindo s1 ON u.id = s1.id_seguindo
                    JOIN seguindo s2 ON u.id = s2.id_seguidor
                    WHERE s1.id_seguidor = %s AND s2.id_seguindo = %s
                    AND NOT EXISTS (
                        SELECT 1 FROM bloqueados 
                        WHERE (usuario_id = %s AND bloqueado_id = u.id)
                        OR (usuario_id = u.id AND bloqueado_id = %s)
                    )
                    ORDER BY u.username
                """, (usuario_id, usuario_id, usuario_id, usuario_id))
                
                usuarios = cursor.fetchall()
                
                # Formatar as URLs das fotos de perfil
                for usuario in usuarios:
                    if usuario['fotos_perfil']:
                        usuario['foto_perfil'] = url_for('static', filename=usuario['fotos_perfil'])
                
                return jsonify({
                    'success': True,
                    'usuarios': usuarios
                })
        
        return jsonify({'success': False, 'message': 'Erro na conexão com o banco de dados'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@enviar_post_chat_bp.route('/enviar_post_para_chat', methods=['POST'])
def enviar_post_para_chat():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'Não autenticado'})

    usuario_id = session['usuario_id']
    post_id = request.form.get('post_id')
    destinatario_id = request.form.get('usuario_id')

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Verificar se o post existe e pertence a um usuário visível
                cursor.execute("""
                    SELECT p.id, p.users_id
                    FROM posts p
                    JOIN users u ON p.users_id = u.id
                    WHERE p.id = %s
                    AND NOT EXISTS (
                        SELECT 1 FROM bloqueados 
                        WHERE (usuario_id = %s AND bloqueado_id = p.users_id)
                        OR (usuario_id = p.users_id AND bloqueado_id = %s)
                    )
                """, (post_id, usuario_id, usuario_id))
                
                post = cursor.fetchone()
                if not post:
                    return jsonify({'success': False, 'message': 'Post não encontrado ou acesso negado'})

                # Verificar se o destinatário pode ver o post
                cursor.execute("""
                    SELECT 1 FROM users WHERE id = %s AND (
                        perfil_publico = 1
                        OR id = %s
                        OR EXISTS (
                            SELECT 1 FROM seguindo 
                            WHERE id_seguidor = %s AND id_seguindo = %s
                        )
                    )
                """, (destinatario_id, post['users_id'], destinatario_id, post['users_id']))
                
                if not cursor.fetchone():
                    return jsonify({'success': False, 'message': 'O destinatário não pode ver este post'})

                # Inserir mensagem no chat com referência ao post
                mensagem = "Confira este post"
                cursor.execute("""
                    INSERT INTO mensagens 
                    (id_remetente, id_destinatario, post_id, mensagem, data_envio)
                    VALUES (%s, %s, %s, %s, NOW())
                """, (usuario_id, destinatario_id, post_id, mensagem))
                
                conexao.commit()
                return jsonify({'success': True, 'message': 'Post compartilhado com sucesso'})
        
        return jsonify({'success': False, 'message': 'Erro na conexão com o banco de dados'})
    
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}) 