from flask import Flask, Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
import os
from werkzeug.utils import secure_filename
from app.conexao import criar_conexao  # Importe a função de conexão com o banco de dados
from datetime import datetime, timedelta

def formatar_data(data):
    hoje = datetime.now().date()
    ontem = hoje - timedelta(days=1)

    if data.date() == hoje:
        return "Hoje"
    elif data.date() == ontem:
        return "Ontem"
    else:
        # Dicionário para mapear números de meses para nomes
        meses = {
            1: "janeiro", 2: "fevereiro", 3: "março", 4: "abril",
            5: "maio", 6: "junho", 7: "julho", 8: "agosto",
            9: "setembro", 10: "outubro", 11: "novembro", 12: "dezembro"
        }

        # Extrai o dia, mês e ano
        dia = data.day
        mes = meses[data.month]
        ano = data.year

        # Retorna a data formatada
        return f"{dia} de {mes} de {ano}"


# Blueprint para o chat
chat_bp = Blueprint('chat', __name__)

UPLOAD_FOLDER_VIDEOS = '../static/img/uploads/chat/video'
UPLOAD_FOLDER_FOTOS = '../static/img/uploads/chat/foto'
ALLOWED_EXTENSIONS_FOTOS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_EXTENSIONS_VIDEOS = {'mp4', 'mov', 'avi'}

def allowed_file(filename, allowed_extensions):
      return '.' in filename and \
             filename.rsplit('.', 1)[1].lower() in allowed_extensions

@chat_bp.route('/chat')
def chat():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Informações do usuário
                cursor.execute("SELECT fotos_perfil, audio_notificacoes_mensagem, tema FROM users WHERE id = %s", (usuario_id,))
                usuario = cursor.fetchone()
                foto_perfil = usuario['fotos_perfil'] if usuario and usuario['fotos_perfil'] else url_for('static', filename='img/icone/user.png')
                audio_notificacoes_mensagem = usuario['audio_notificacoes_mensagem'] if usuario and usuario['audio_notificacoes_mensagem'] is not None else True

                if usuario:
                    tema = usuario.get('tema', 'claro')  # agora funciona
                else:
                    tema = 'claro'

                # Buscar as pessoas que você segue
                cursor.execute("""
                    SELECT u.id, u.username, u.fotos_perfil,
                        COALESCE(MAX(m.data_envio), '1900-01-01') as ultima_mensagem
                    FROM users u
                    JOIN seguindo s1 ON u.id = s1.id_seguindo
                    JOIN seguindo s2 ON u.id = s2.id_seguidor AND s2.id_seguindo = s1.id_seguidor
                    LEFT JOIN mensagens m ON
                        ((m.id_remetente = u.id AND m.id_destinatario = %s) OR
                        (m.id_destinatario = u.id AND m.id_remetente = %s))
                    WHERE s1.id_seguidor = %s
                    GROUP BY u.id, u.username, u.fotos_perfil
                    ORDER BY ultima_mensagem DESC
                """, (usuario_id, usuario_id, usuario_id))
                seguindo_lista = cursor.fetchall()

                cursor.execute("""
                    SELECT u.id, u.username, u.fotos_perfil,
                        COALESCE(MAX(m.data_envio), '1900-01-01') as ultima_mensagem
                    FROM users u
                    JOIN seguindo s1 ON u.id = s1.id_seguindo
                    JOIN seguindo s2 ON u.id = s2.id_seguidor AND s2.id_seguindo = s1.id_seguidor
                    LEFT JOIN mensagens m ON
                        ((m.id_remetente = u.id AND m.id_destinatario = %s) OR
                        (m.id_destinatario = u.id AND m.id_remetente = %s))
                    WHERE s1.id_seguidor = %s
                    GROUP BY u.id, u.username, u.fotos_perfil
                    ORDER BY ultima_mensagem DESC
                """, (usuario_id, usuario_id, usuario_id))
                seguidores_lista = cursor.fetchall()

                # Filtrar a lista de contatos para incluir apenas os usuários que estão em ambas as listas (seguidos e seguidores)
                contatos = [usuario for usuario in seguindo_lista if usuario in seguidores_lista]

                # Adicionar informações extra para cada contato
                for contato in contatos:
                    # Última mensagem (texto, mídia, hora)
                    cursor.execute("""
                        SELECT mensagem, caminho_arquivo, data_envio
                        FROM mensagens
                        WHERE (id_remetente = %s AND id_destinatario = %s)
                           OR (id_remetente = %s AND id_destinatario = %s)
                        ORDER BY data_envio DESC
                        LIMIT 1
                    """, (usuario_id, contato['id'], contato['id'], usuario_id))
                    ultima = cursor.fetchone()
                    if ultima:
                        contato['ultima_mensagem'] = ultima['mensagem']
                        contato['ultima_midia'] = ultima['caminho_arquivo']
                        contato['ultima_hora'] = ultima['data_envio'].strftime('%H:%M') if ultima['data_envio'] else ""
                    else:
                        contato['ultima_mensagem'] = ""
                        contato['ultima_midia'] = ""
                        contato['ultima_hora'] = ""
                    
                    # Mensagens não lidas
                    cursor.execute("""
                        SELECT COUNT(*) as nao_vistas
                        FROM mensagens
                        WHERE id_remetente = %s AND id_destinatario = %s AND data_visualizacao IS NULL
                    """, (contato['id'], usuario_id))
                    contato['nao_vistas'] = cursor.fetchone()['nao_vistas']

            conexao.close()

            return render_template(
                'conversa.html',
                contatos=contatos,
                usuario_id=usuario_id,
                foto_perfil=foto_perfil,
                 audio_notificacoes_mensagem=audio_notificacoes_mensagem,
                 tema=tema
            )

        return "Erro na conexão com o banco de dados."

    except Exception as e:
        return f"Erro ao conectar ao banco de dados: {str(e)}"

@chat_bp.route('/chat/<int:destinatario_id>', methods=['GET'])
def chat_conversa(destinatario_id):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    if destinatario_id == usuario_id:
        return redirect(url_for('chat.chat'))

    try:
        conexao = criar_conexao()

        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Verificar se os usuários se seguem mutuamente
                cursor.execute("""
                    SELECT COUNT(*) as mutual_follow
                    FROM seguindo s1
                    JOIN seguindo s2 ON s1.id_seguidor = s2.id_seguindo AND s1.id_seguindo = s2.id_seguidor
                    WHERE s1.id_seguidor = %s AND s1.id_seguindo = %s
                """, (usuario_id, destinatario_id))
                mutual_follow = cursor.fetchone()['mutual_follow']

                if not mutual_follow:
                    return redirect(url_for('chat.chat'))

                # Informações do usuário logado
                cursor.execute("SELECT fotos_perfil, tema FROM users WHERE id = %s", (usuario_id,))
                usuario = cursor.fetchone()
                foto_perfil = usuario['fotos_perfil'] if usuario and usuario['fotos_perfil'] else url_for('static', filename='img/icone/user.png')

                if usuario:
                    tema = usuario.get('tema', 'claro')  # agora funciona
                else:
                    tema = 'claro'

                # Mensagens da conversa
                cursor.execute("""
                    SELECT 
                        m.id, 
                        m.mensagem, 
                        m.data_envio, 
                        u.username, 
                        u.fotos_perfil, 
                        m.id_remetente,
                        DATE(m.data_envio) as data_dia, 
                        m.caminho_arquivo, 
                        m.id_mensagem_respondida,
                        m.post_id,
                        m.data_visualizacao,       
                        p.conteudo as post_conteudo,
                        p.imagem as post_imagem,
                        p.video as post_video,
                        p.users_id as post_autor_id,
                        up.username as post_autor_username,
                        up.perfil_publico as post_autor_publico,
                        CASE 
                            WHEN p.id IS NULL THEN 0
                            WHEN EXISTS (
                                SELECT 1 FROM bloqueados 
                                WHERE (usuario_id = %s AND bloqueado_id = p.users_id) 
                                OR (usuario_id = p.users_id AND bloqueado_id = %s)
                            ) THEN 0
                            WHEN p.users_id != %s AND up.perfil_publico = 0 AND NOT EXISTS (
                                SELECT 1 FROM seguindo 
                                WHERE id_seguidor = %s AND id_seguindo = p.users_id
                            ) THEN 0
                            ELSE 1
                        END as post_disponivel,
                        CASE 
                            WHEN m.id_mensagem_respondida IS NOT NULL AND mr.id IS NULL THEN 'Mensagem apagada'
                            ELSE mr.mensagem 
                        END as mensagem_respondida,
                        CASE
                            WHEN m.id_mensagem_respondida IS NOT NULL AND mr.id IS NULL THEN NULL
                            ELSE ur.username
                        END as username_respondido,
                        CASE
                            WHEN m.id_mensagem_respondida IS NOT NULL AND mr.id IS NULL THEN NULL
                            ELSE ur.fotos_perfil
                        END as foto_respondido,
                        CASE
                            WHEN m.id_mensagem_respondida IS NOT NULL AND mr.id IS NULL THEN NULL
                            ELSE mr.caminho_arquivo
                        END as midia_respondida
                    FROM mensagens m
                    JOIN users u ON m.id_remetente = u.id
                    LEFT JOIN mensagens mr ON m.id_mensagem_respondida = mr.id
                    LEFT JOIN users ur ON mr.id_remetente = ur.id
                    LEFT JOIN posts p ON m.post_id = p.id
                    LEFT JOIN users up ON p.users_id = up.id
                    WHERE (m.id_remetente = %s AND m.id_destinatario = %s)
                    OR (m.id_remetente = %s AND m.id_destinatario = %s)
                    ORDER BY m.data_envio
                """, (usuario_id, usuario_id, usuario_id, usuario_id, usuario_id, destinatario_id, destinatario_id, usuario_id))
                mensagens = cursor.fetchall()

                # Informações do destinatário
                cursor.execute("SELECT username, fotos_perfil, online FROM users WHERE id = %s", (destinatario_id,))
                destinatario = cursor.fetchone()
                destinatario_username = destinatario['username']
                destinatario_foto_perfil = destinatario['fotos_perfil']
                destinatario_online = destinatario['online']

                # Buscar as pessoas que você segue
                cursor.execute("""
                    SELECT u.id, u.username, u.fotos_perfil,
                        COALESCE(MAX(m.data_envio), '1900-01-01') as ultima_mensagem
                    FROM users u
                    JOIN seguindo s1 ON u.id = s1.id_seguindo
                    JOIN seguindo s2 ON u.id = s2.id_seguidor AND s2.id_seguindo = s1.id_seguidor
                    LEFT JOIN mensagens m ON
                        ((m.id_remetente = u.id AND m.id_destinatario = %s) OR
                        (m.id_destinatario = u.id AND m.id_remetente = %s))
                    WHERE s1.id_seguidor = %s
                    GROUP BY u.id, u.username, u.fotos_perfil
                    ORDER BY ultima_mensagem DESC
                """, (usuario_id, usuario_id, usuario_id))
                seguindo_lista = cursor.fetchall()

                cursor.execute("""
                    SELECT u.id, u.username, u.fotos_perfil,
                        COALESCE(MAX(m.data_envio), '1900-01-01') as ultima_mensagem
                    FROM users u
                    JOIN seguindo s1 ON u.id = s1.id_seguindo
                    JOIN seguindo s2 ON u.id = s2.id_seguidor AND s2.id_seguindo = s1.id_seguidor
                    LEFT JOIN mensagens m ON
                        ((m.id_remetente = u.id AND m.id_destinatario = %s) OR
                        (m.id_destinatario = u.id AND m.id_remetente = %s))
                    WHERE s1.id_seguidor = %s
                    GROUP BY u.id, u.username, u.fotos_perfil
                    ORDER BY ultima_mensagem DESC
                """, (usuario_id, usuario_id, usuario_id))
                seguidores_lista = cursor.fetchall()

                # Filtrar a lista de contatos para incluir apenas os usuários que estão em ambas as listas (seguidos e seguidores)
                contatos = [usuario for usuario in seguindo_lista if usuario in seguidores_lista]

                # Adicionar informações extra para cada contato
                for contato in contatos:
                    # Última mensagem (texto, mídia, hora)
                    cursor.execute("""
                        SELECT mensagem, caminho_arquivo, data_envio
                        FROM mensagens
                        WHERE (id_remetente = %s AND id_destinatario = %s)
                           OR (id_remetente = %s AND id_destinatario = %s)
                        ORDER BY data_envio DESC
                        LIMIT 1
                    """, (usuario_id, contato['id'], contato['id'], usuario_id))
                    ultima = cursor.fetchone()
                    if ultima:
                        contato['ultima_mensagem'] = ultima['mensagem']
                        contato['ultima_midia'] = ultima['caminho_arquivo']
                        contato['ultima_hora'] = ultima['data_envio'].strftime('%H:%M') if ultima['data_envio'] else ""
                    else:
                        contato['ultima_mensagem'] = ""
                        contato['ultima_midia'] = ""
                        contato['ultima_hora'] = ""
                    
                    # Mensagens não lidas
                    cursor.execute("""
                        SELECT COUNT(*) as nao_vistas
                        FROM mensagens
                        WHERE id_remetente = %s AND id_destinatario = %s AND data_visualizacao IS NULL
                    """, (contato['id'], usuario_id))
                    contato['nao_vistas'] = cursor.fetchone()['nao_vistas']

            conexao.close()

            conexao.close()

            return render_template(
                'conversa.html',
                mensagens=mensagens,
                destinatario_id=destinatario_id,
                destinatario_username=destinatario_username,
                destinatario_foto_perfil=destinatario_foto_perfil,
                destinatario_online=destinatario_online,
                contatos=contatos,
                usuario_id=usuario_id,
                foto_perfil=foto_perfil,
                tema=tema
            )

        return "Erro na conexão com o banco de dados."

    except Exception as e:
        return f"Erro ao carregar a conversa: {str(e)}"

#==================== 
#PARA ENVIAR MENSAGEM
#==================== 
@chat_bp.route('/enviar', methods=['POST'])
def enviar_mensagem():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'error': 'Usuário não autenticado'})

    usuario_id = session['usuario_id']
    destinatario_id = request.form.get('destinatario_id')
    mensagem = request.form.get('mensagem', '')
    id_mensagem_respondida = request.form.get('id_mensagem_respondida', None)
    tem_midia = False
    caminho_arquivo = None

    if 'foto' in request.files:
        foto = request.files['foto']
        if foto.filename != '' and allowed_file(foto.filename, ALLOWED_EXTENSIONS_FOTOS):
            filename = secure_filename(foto.filename)
            caminho_foto = os.path.join(chat_bp.root_path, UPLOAD_FOLDER_FOTOS, filename)
            foto.save(caminho_foto)
            caminho_arquivo = os.path.join('img/uploads/chat/foto', filename)
            tem_midia = True

    if 'video' in request.files:
        video = request.files['video']
        if video.filename != '' and allowed_file(video.filename, ALLOWED_EXTENSIONS_VIDEOS):
            filename = secure_filename(video.filename)
            caminho_video = os.path.join(chat_bp.root_path, UPLOAD_FOLDER_VIDEOS, filename)
            video.save(caminho_video)
            caminho_arquivo = os.path.join('img/uploads/chat/video', filename)
            tem_midia = True

    if not mensagem and not tem_midia:
        return jsonify({'success': False, 'error': 'A mensagem não pode estar vazia se não houver mídia.'})

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT id FROM users WHERE id = %s", (destinatario_id,))
                destinatario = cursor.fetchone()

                if not destinatario:
                    return jsonify({'success': False, 'error': 'Destinatário não encontrado'})

                cursor.execute("""
                    INSERT INTO mensagens (id_remetente, id_destinatario, mensagem, caminho_arquivo, id_mensagem_respondida)
                    VALUES (%s, %s, %s, %s, %s)
                """, (usuario_id, destinatario_id, mensagem, caminho_arquivo, id_mensagem_respondida))

                conexao.commit()

                cursor.execute("""
                    SELECT u.username, m.data_envio, m.caminho_arquivo, m.id_mensagem_respondida
                    FROM mensagens m
                    JOIN users u ON m.id_remetente = u.id
                    WHERE m.id_remetente = %s AND m.id_destinatario = %s
                    ORDER BY m.data_envio DESC
                    LIMIT 1
                """, (usuario_id, destinatario_id))
                resultado = cursor.fetchone()

                if resultado:
                    username = resultado['username']
                    timestamp = resultado['data_envio'].strftime('%H:%M')
                    caminho_arquivo_retornado = resultado['caminho_arquivo']
                    id_mensagem_respondida_retornado = resultado['id_mensagem_respondida']
                    
                    # Buscar dados da mensagem respondida se existir
                    mensagem_respondida = None
                    if id_mensagem_respondida_retornado:
                        cursor.execute("""
                            SELECT m.id, m.mensagem, u.username
                            FROM mensagens m
                            JOIN users u ON m.id_remetente = u.id
                            WHERE m.id = %s
                        """, (id_mensagem_respondida_retornado,))
                        mensagem_respondida = cursor.fetchone()

            conexao.close()

            return jsonify({
                'success': True,
                'mensagem': mensagem,
                'username': username,
                'timestamp': timestamp,
                'caminho_arquivo': caminho_arquivo_retornado,
                'id_mensagem_respondida': id_mensagem_respondida_retornado,
                'mensagem_respondida': mensagem_respondida
            })

        return jsonify({'success': False, 'error': 'Erro na conexão com o banco de dados.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@chat_bp.route('/atualizar_mensagens/<int:destinatario_id>', methods=['GET'])
def atualizar_mensagens(destinatario_id):
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'error': 'Usuário não autenticado'})

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()

        if conexao:
            with conexao.cursor(dictionary=True) as cursor:

                cursor.execute("""
                    UPDATE mensagens
                    SET data_visualizacao = NOW()
                    WHERE id_destinatario = %s AND id_remetente = %s AND data_visualizacao IS NULL
                """, (usuario_id, destinatario_id))
                conexao.commit()

                cursor.execute("""
                    SELECT 
                        m.id, 
                        m.mensagem, 
                        m.data_envio, 
                        u.username, 
                        u.fotos_perfil, 
                        m.id_remetente,
                        DATE(m.data_envio) as data_dia, 
                        m.caminho_arquivo, 
                        m.id_mensagem_respondida,
                        m.post_id,
                        m.data_visualizacao,
                        CASE 
                WHEN m.data_visualizacao IS NOT NULL THEN 1
                ELSE 0
            END as foi_visualizada,              
                        p.conteudo as post_conteudo,
                        p.imagem as post_imagem,
                        p.video as post_video,
                        p.users_id as post_autor_id,
                        up.username as post_autor_username,
                        up.perfil_publico as post_autor_publico,
                        CASE 
                            WHEN p.id IS NULL THEN 0
                            WHEN EXISTS (
                                SELECT 1 FROM bloqueados 
                                WHERE (usuario_id = %s AND bloqueado_id = p.users_id) 
                                OR (usuario_id = p.users_id AND bloqueado_id = %s)
                            ) THEN 0
                            WHEN p.users_id != %s AND up.perfil_publico = 0 AND NOT EXISTS (
                                SELECT 1 FROM seguindo 
                                WHERE id_seguidor = %s AND id_seguindo = p.users_id
                            ) THEN 0
                            ELSE 1
                        END as post_disponivel,
                        CASE 
                            WHEN m.id_mensagem_respondida IS NOT NULL AND mr.id IS NULL THEN 'Mensagem apagada'
                            ELSE mr.mensagem 
                        END as mensagem_respondida,
                        CASE
                            WHEN m.id_mensagem_respondida IS NOT NULL AND mr.id IS NULL THEN NULL
                            ELSE ur.username
                        END as username_respondido,
                        CASE
                            WHEN m.id_mensagem_respondida IS NOT NULL AND mr.id IS NULL THEN NULL
                            ELSE ur.fotos_perfil
                        END as foto_respondido,
                        CASE
                            WHEN m.id_mensagem_respondida IS NOT NULL AND mr.id IS NULL THEN NULL
                            ELSE mr.caminho_arquivo
                        END as midia_respondida
                    FROM mensagens m
                    JOIN users u ON m.id_remetente = u.id
                    LEFT JOIN mensagens mr ON m.id_mensagem_respondida = mr.id
                    LEFT JOIN users ur ON mr.id_remetente = ur.id
                    LEFT JOIN posts p ON m.post_id = p.id
                    LEFT JOIN users up ON p.users_id = up.id
                    WHERE (m.id_remetente = %s AND m.id_destinatario = %s)
                    OR (m.id_remetente = %s AND m.id_destinatario = %s)
                    ORDER BY m.data_envio
                """, (usuario_id, usuario_id, usuario_id, usuario_id, usuario_id, destinatario_id, destinatario_id, usuario_id))
                mensagens = cursor.fetchall()

                for mensagem in mensagens:
                    mensagem['data_envio'] = mensagem['data_envio'].strftime('%H:%M')
                    data_dia = datetime.strptime(str(mensagem['data_dia']), '%Y-%m-%d')
                    mensagem['data_dia'] = formatar_data(data_dia)

            conexao.close()

            return jsonify({'success': True, 'mensagens': mensagens})

        return jsonify({'success': False, 'error': 'Erro na conexão com o banco de dados.'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@chat_bp.route('/deletar_mensagem/<int:mensagem_id>', methods=['DELETE'])
def deletar_mensagem(mensagem_id):
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'error': 'Usuário não autenticado'})

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()

        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Verificar se a mensagem pertence ao usuário e obter informações adicionais
                cursor.execute("""
                    SELECT id_remetente, id_destinatario 
                    FROM mensagens 
                    WHERE id = %s
                """, (mensagem_id,))
                mensagem = cursor.fetchone()

                if not mensagem:
                    return jsonify({'success': False, 'error': 'Mensagem não encontrada'})

                if mensagem['id_remetente'] != usuario_id:
                    return jsonify({'success': False, 'error': 'Você não tem permissão para apagar esta mensagem'})

                # Obter o ID do outro usuário na conversa
                outro_usuario_id = mensagem['id_destinatario'] if mensagem['id_remetente'] == usuario_id else mensagem['id_remetente']

                # Deletar a mensagem
                cursor.execute("DELETE FROM mensagens WHERE id = %s", (mensagem_id,))
                conexao.commit()

                # Retornar informações adicionais para atualização
                return jsonify({
                    'success': True,
                    'mensagem_id': mensagem_id,
                    'outro_usuario_id': outro_usuario_id
                })

        return jsonify({'success': False, 'error': 'Erro na conexão com o banco de dados.'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}) 
    
@chat_bp.route('/verificar_mensagens/<int:destinatario_id>', methods=['GET'])
def verificar_mensagens(destinatario_id):
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'error': 'Usuário não autenticado'})

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()

        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Buscar as mensagens entre o usuário e o destinatário
                cursor.execute("""
                    SELECT m.id, m.mensagem, m.data_envio, u.username, u.fotos_perfil, m.id_remetente,
                           DATE(m.data_envio) as data_dia, m.caminho_arquivo
                    FROM mensagens m
                    JOIN users u ON m.id_remetente = u.id
                    WHERE (m.id_remetente = %s AND m.id_destinatario = %s)
                       OR (m.id_remetente = %s AND m.id_destinatario = %s)
                    ORDER BY m.data_envio
                """, (usuario_id, destinatario_id, destinatario_id, usuario_id))
                mensagens = cursor.fetchall()

                # Formatar a data_envio para exibir apenas a hora e o minuto
                for mensagem in mensagens:
                    mensagem['data_envio'] = mensagem['data_envio'].strftime('%H:%M')
                    data_dia = datetime.strptime(str(mensagem['data_dia']), '%Y-%m-%d')  # Converte para objeto datetime
                    mensagem['data_dia'] = formatar_data(data_dia)  # Formata a data

            conexao.close()

            return jsonify({'success': True, 'mensagens': mensagens})

        return jsonify({'success': False, 'error': 'Erro na conexão com o banco de dados.'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@chat_bp.route('/api/nao_vistas', methods=['GET'])
def contar_nao_vistas():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'error': 'Usuário não autenticado'})
    usuario_id = session['usuario_id']
    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT m.id_remetente as contato_id, COUNT(*) as nao_vistas
                    FROM mensagens m
                    WHERE m.id_destinatario = %s AND m.data_visualizacao IS NULL
                    GROUP BY m.id_remetente
                """, (usuario_id,))
                resultado = cursor.fetchall()
            conexao.close()
            # Transforma em dicionário para facilitar no JS
            counts = {str(row['contato_id']): row['nao_vistas'] for row in resultado}
            return jsonify({'success': True, 'counts': counts})
        return jsonify({'success': False, 'error': 'Erro na conexão com o banco de dados.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@chat_bp.route('/api/ultimas_msgs', methods=['GET'])
def ultimas_msgs():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'error': 'Usuário não autenticado'})
    usuario_id = session['usuario_id']
    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                cursor.execute("""
                    SELECT u.id as contato_id, u.username, u.fotos_perfil,
                        (SELECT mensagem FROM mensagens m
                            WHERE (m.id_remetente = u.id AND m.id_destinatario = %s)
                               OR (m.id_remetente = %s AND m.id_destinatario = u.id)
                            ORDER BY m.data_envio DESC LIMIT 1
                        ) as ultima_mensagem,
                        (SELECT caminho_arquivo FROM mensagens m
                            WHERE (m.id_remetente = u.id AND m.id_destinatario = %s)
                               OR (m.id_remetente = %s AND m.id_destinatario = u.id)
                            ORDER BY m.data_envio DESC LIMIT 1
                        ) as ultima_midia,
                        (SELECT data_envio FROM mensagens m
                            WHERE (m.id_remetente = u.id AND m.id_destinatario = %s)
                               OR (m.id_remetente = %s AND m.id_destinatario = u.id)
                            ORDER BY m.data_envio DESC LIMIT 1
                        ) as ultima_hora
                    FROM users u
                    JOIN seguindo s1 ON u.id = s1.id_seguindo
                    JOIN seguindo s2 ON u.id = s2.id_seguidor AND s2.id_seguindo = s1.id_seguidor
                    WHERE s1.id_seguidor = %s
                """, (usuario_id, usuario_id, usuario_id, usuario_id, usuario_id, usuario_id, usuario_id))
                contatos = cursor.fetchall()
            conexao.close()
            # Formata datas e prepara para o JSON
            for contato in contatos:
                contato['ultima_hora'] = contato['ultima_hora'].strftime('%H:%M') if contato['ultima_hora'] else ""
            return jsonify({'success': True, 'contatos': contatos})
        return jsonify({'success': False, 'error': 'Erro na conexão com o banco de dados.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
@chat_bp.route('/api/status_usuario/<int:usuario_id>')
def status_usuario(usuario_id):
    from datetime import datetime, timedelta
    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT ultima_atividade, modo_status FROM users WHERE id = %s", (usuario_id,))
                user = cursor.fetchone()
            conexao.close()
            if user:
                if user.get('modo_status', 'normal') == 'ausente':
                    return jsonify({'online': False})  # Sempre off
                ultima_atividade = user['ultima_atividade']
                agora = datetime.now()
                online = (agora - ultima_atividade) < timedelta(seconds=60)
                return jsonify({'online': online})
        return jsonify({'online': False})
    except Exception as e:
        return jsonify({'online': False, 'error': str(e)})
    
@chat_bp.route('/api/status_visto/<int:destinatario_id>')
def status_visto(destinatario_id):
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'error': 'Usuário não autenticado'})
    usuario_id = session['usuario_id']
    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Apenas mensagens enviadas pelo usuário logado para o destinatário
                cursor.execute("""
                    SELECT id, data_visualizacao
                    FROM mensagens
                    WHERE id_remetente = %s AND id_destinatario = %s
                """, (usuario_id, destinatario_id))
                msgs = cursor.fetchall()
            conexao.close()
            # Retorna um dicionário: {id: True/False}
            status = {str(m['id']): bool(m['data_visualizacao']) for m in msgs}
            return jsonify({'success': True, 'status': status})
        return jsonify({'success': False})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})