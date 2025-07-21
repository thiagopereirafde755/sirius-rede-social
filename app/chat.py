from flask import  Blueprint, render_template, redirect, url_for, session, request, jsonify
import os
from app.conexao import criar_conexao 
from app.utils import  buscar_info_usuario_logado_chat, buscar_contatos, data_msg
import cloudinary.uploader
from dotenv import load_dotenv
import traceback
import cloudinary

chat_bp = Blueprint('chat', __name__)

# =============================================================
#  CONFIGURAÇAO DA CLOUDINARY
# =============================================================
load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# FORMATOS ACEITO
ALLOWED_EXTENSIONS_FOTOS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp', 'svg', 'heic', 'heif', 'jfif','ico','raw','psd','exr','dng'}
ALLOWED_EXTENSIONS_VIDEOS = {'mp4', 'mov', 'avi', 'mkv', 'wmv', 'flv', 'webm', 'mpeg', '3gp', 'ogg', 'm4v','mts','m2ts','vob','mpg','divx','asf','3g2','f4v'}


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
# =============================================================
#  PAGINA INICIAL DO CHAT
# =============================================================
@chat_bp.route('/chat')
def chat():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:

                # INFORMAÇÃO DO USER LOGADO
                foto_perfil, audio_notificacoes_mensagem, tema = buscar_info_usuario_logado_chat(usuario_id)

                # LISTA DE CONTATO
                contatos = buscar_contatos(usuario_id)

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
# =============================================================
#  PAGINA DO CHAT DE CONVERSA
# =============================================================
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

                # VERIFICA SE SAO AMIGOS
                cursor.execute("""
                    SELECT COUNT(*) as mutual_follow
                    FROM seguindo s1
                    JOIN seguindo s2 ON s1.id_seguidor = s2.id_seguindo AND s1.id_seguindo = s2.id_seguidor
                    WHERE s1.id_seguidor = %s AND s1.id_seguindo = %s
                """, (usuario_id, destinatario_id))
                mutual_follow = cursor.fetchone()['mutual_follow']

                if not mutual_follow:
                    return redirect(url_for('chat.chat'))

                # INFORMAÇÃO DO USER LOGADO
                foto_perfil, audio_notificacoes_mensagem, tema = buscar_info_usuario_logado_chat(usuario_id)

                # MENSAGENS DA CONVERSA
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
                            WHEN up.suspenso = 1 THEN 0
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
                    WHERE 
                        u.suspenso = 0
                        AND (
                            (m.id_remetente = %s AND m.id_destinatario = %s)
                            OR (m.id_remetente = %s AND m.id_destinatario = %s)
                        )
                    ORDER BY m.data_envio
                """, (usuario_id, usuario_id, usuario_id, usuario_id, usuario_id, destinatario_id, destinatario_id, usuario_id))

                mensagens = cursor.fetchall()

                # INFORMAÇAO DO DESTINATARIO
                cursor.execute("SELECT username, fotos_perfil, online FROM users WHERE id = %s", (destinatario_id,))
                destinatario = cursor.fetchone()
                destinatario_username = destinatario['username']
                destinatario_foto_perfil = destinatario['fotos_perfil']
                destinatario_online = destinatario['online']

                # Contar total de mensagens trocadas entre os dois
                cursor.execute("""
                    SELECT COUNT(*) as total
                    FROM mensagens
                    WHERE (id_remetente = %s AND id_destinatario = %s)
                    OR (id_remetente = %s AND id_destinatario = %s)
                """, (usuario_id, destinatario_id, destinatario_id, usuario_id))
                total_mensagens_trocadas = cursor.fetchone()['total']

                # LISTA DE CONTATO
                contatos = buscar_contatos(usuario_id)

            conexao.close()

            conexao.close()

            return render_template(
                'conversa.html',
                mensagens=mensagens,
                total_mensagens_trocadas=total_mensagens_trocadas,
                destinatario_id=destinatario_id,
                destinatario_username=destinatario_username,
                destinatario_foto_perfil=destinatario_foto_perfil,
                destinatario_online=destinatario_online,
                contatos=contatos,
                usuario_id=usuario_id,
                foto_perfil=foto_perfil,
                tema=tema,
                audio_notificacoes_mensagem=audio_notificacoes_mensagem,
            )

        return "Erro na conexão com o banco de dados."

    except Exception as e:
        return f"Erro ao carregar a conversa: {str(e)}"
# =============================================================
#  PARA ENVIAR AS MENSAGENS
# =============================================================
@chat_bp.route('/enviar', methods=['POST'])
def enviar_mensagem():
    print("[LOG] Início do envio de mensagem")
    if 'usuario_id' not in session:
        print("[LOG] Usuário não autenticado")
        return jsonify({'success': False, 'error': 'Usuário não autenticado'})

    usuario_id = session['usuario_id']
    destinatario_id = request.form.get('destinatario_id')
    mensagem = request.form.get('mensagem', '').strip()
    id_mensagem_respondida = request.form.get('id_mensagem_respondida', None)
    tem_midia = False
    url_midia = None
    tipo_midia = None  
    public_id = None

    print(f"[LOG] Usuário {usuario_id} enviando para destinatário {destinatario_id}")
    print(f"[LOG] Mensagem recebida: '{mensagem}'")

    # FOTO
    if 'foto' in request.files:
        foto = request.files['foto']
        print(f"[LOG] Arquivo foto recebido: {foto.filename}")
        if foto.filename != '' and allowed_file(foto.filename, ALLOWED_EXTENSIONS_FOTOS):
            try:
                upload_result = cloudinary.uploader.upload(
                    foto,
                    folder='chat/fotos',
                    resource_type='image'
                )
                url_midia = upload_result.get('secure_url')
                public_id = upload_result.get('public_id')
                tem_midia = True
                tipo_midia = 'foto'
                print(f"[LOG] Foto enviada para Cloudinary: {url_midia}")
            except Exception as e:
                print(f"[ERRO] Falha no upload da foto: {e}")
                return jsonify({'success': False, 'error': f'Erro ao enviar foto: {str(e)}'})

    # VIDEO
    if 'video' in request.files:
        video = request.files['video']
        print(f"[LOG] Arquivo vídeo recebido: {video.filename}")
        if video.filename != '' and allowed_file(video.filename, ALLOWED_EXTENSIONS_VIDEOS):
            try:
                upload_result = cloudinary.uploader.upload(
                    video,
                    folder='chat/videos',
                    resource_type='video'
                )
                url_midia = upload_result.get('secure_url')
                public_id = upload_result.get('public_id')
                tem_midia = True
                tipo_midia = 'video'
                print(f"[LOG] Vídeo enviado para Cloudinary: {url_midia}")
            except Exception as e:
                print(f"[ERRO] Falha no upload do vídeo: {e}")
                return jsonify({'success': False, 'error': f'Erro ao enviar vídeo: {str(e)}'})

    if not mensagem and not tem_midia:
        print("[LOG] Mensagem vazia e sem mídia, abortando envio")
        return jsonify({'success': False, 'error': 'A mensagem não pode estar vazia se não houver mídia.'})

    try:
        conexao = criar_conexao()
        if not conexao:
            print("[ERRO] Falha na conexão com o banco de dados")
            return jsonify({'success': False, 'error': 'Erro na conexão com o banco de dados.'})

        with conexao.cursor(dictionary=True) as cursor:

            # VERIFICA SE O DESTINATARIO EXISTE
            cursor.execute("SELECT id FROM users WHERE id = %s", (destinatario_id,))
            destinatario = cursor.fetchone()
            if not destinatario:
                print(f"[ERRO] Destinatário {destinatario_id} não encontrado")
                return jsonify({'success': False, 'error': 'Destinatário não encontrado'})

            # SALVA NO BANCO
            cursor.execute("""
                INSERT INTO mensagens (id_remetente, id_destinatario, mensagem, caminho_arquivo, public_id, id_mensagem_respondida)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (usuario_id, destinatario_id, mensagem or None, url_midia, public_id, id_mensagem_respondida))

            conexao.commit()
            print("[LOG] Mensagem inserida no banco de dados")

            # Busca a mensagem recém inserida para retorno
            cursor.execute("""
                SELECT u.username, m.data_envio, m.caminho_arquivo, m.id_mensagem_respondida
                FROM mensagens m
                JOIN users u ON m.id_remetente = u.id
                WHERE m.id_remetente = %s AND m.id_destinatario = %s
                ORDER BY m.data_envio DESC
                LIMIT 1
            """, (usuario_id, destinatario_id))
            resultado = cursor.fetchone()

            mensagem_respondida = None
            if resultado and resultado['id_mensagem_respondida']:
                cursor.execute("""
                    SELECT m.id, m.mensagem, u.username
                    FROM mensagens m
                    JOIN users u ON m.id_remetente = u.id
                    WHERE m.id = %s
                """, (resultado['id_mensagem_respondida'],))
                mensagem_respondida = cursor.fetchone()

        conexao.close()

        if not resultado:
            print("[ERRO] Não foi possível recuperar a mensagem enviada")
            return jsonify({'success': False, 'error': 'Erro ao recuperar mensagem enviada.'})

        print(f"[LOG] Mensagem enviada com sucesso por {resultado['username']} às {resultado['data_envio'].strftime('%H:%M')}")
        return jsonify({
            'success': True,
            'mensagem': mensagem,
            'username': resultado['username'],
            'timestamp': resultado['data_envio'].strftime('%H:%M'),
            'caminho_arquivo': resultado['caminho_arquivo'],  # link Cloudinary
            'tipo_midia': tipo_midia,
            'id_mensagem_respondida': resultado['id_mensagem_respondida'],
            'mensagem_respondida': mensagem_respondida
        })

    except Exception as e:
        traceback.print_exc()
        print(f"[ERRO] Exceção ao enviar mensagem: {e}")
        return jsonify({'success': False, 'error': str(e)})
# =============================================================
#  PARA ATUALIZAR AS MENSAGENS
# =============================================================
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
                            WHEN up.suspenso = 1 THEN 0
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
                    WHERE 
                        u.suspenso = 0
                        AND (
                            (m.id_remetente = %s AND m.id_destinatario = %s)
                            OR (m.id_remetente = %s AND m.id_destinatario = %s)
                        )
                    ORDER BY m.data_envio
                """, (usuario_id, usuario_id, usuario_id, usuario_id, usuario_id, destinatario_id, destinatario_id, usuario_id))

                mensagens = cursor.fetchall()

                # FORMATA A DATA DA MSG
                mensagens = data_msg(mensagens)

            conexao.close()

            return jsonify({'success': True, 'mensagens': mensagens})

        return jsonify({'success': False, 'error': 'Erro na conexão com o banco de dados.'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
# =============================================================
#  PARA DELETAR AS MENSAGENS
# =============================================================
@chat_bp.route('/deletar_mensagem/<int:mensagem_id>', methods=['DELETE'])
def deletar_mensagem(mensagem_id):
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'error': 'Usuário não autenticado'})

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()
        if not conexao:
            return jsonify({'success': False, 'error': 'Erro na conexão com o banco de dados.'})

        with conexao.cursor(dictionary=True) as cursor:
            # Busca mensagem e public_id juntos
            cursor.execute("""
                SELECT id_remetente, id_destinatario, public_id
                FROM mensagens
                WHERE id = %s
            """, (mensagem_id,))
            mensagem = cursor.fetchone()

            if not mensagem:
                return jsonify({'success': False, 'error': 'Mensagem não encontrada'})

            if mensagem['id_remetente'] != usuario_id:
                return jsonify({'success': False, 'error': 'Você não tem permissão para apagar esta mensagem'})

            # SE EXISTIR MIDIA APAGA NA CLOUDINARY
            if mensagem['public_id']:
                try:
                    cloudinary.uploader.destroy(mensagem['public_id'], invalidate=True)
                except Exception as e:
                    print(f"[ERRO] Falha ao deletar mídia da Cloudinary: {e}")

            # Obter o outro usuário da conversa
            outro_usuario_id = mensagem['id_destinatario'] if mensagem['id_remetente'] == usuario_id else mensagem['id_remetente']

            # APAGA A MSG DO BD
            cursor.execute("DELETE FROM mensagens WHERE id = %s", (mensagem_id,))
            conexao.commit()

        conexao.close()

        return jsonify({
            'success': True,
            'mensagem_id': mensagem_id,
            'outro_usuario_id': outro_usuario_id
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
# =============================================================
#  PARA VERIFICAR AS MENSAGENS
# =============================================================   
@chat_bp.route('/verificar_mensagens/<int:destinatario_id>', methods=['GET'])
def verificar_mensagens(destinatario_id):
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'error': 'Usuário não autenticado'})

    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()

        if conexao:
            with conexao.cursor(dictionary=True) as cursor:

                # BUSCAR MSG ENTRE OS USER
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


                # FORMATA A DATA DA MSG
                mensagens = data_msg(mensagens)

            conexao.close()

            return jsonify({'success': True, 'mensagens': mensagens})

        return jsonify({'success': False, 'error': 'Erro na conexão com o banco de dados.'})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
# =============================================================
#  MENSAGENS NAO VISTA
# =============================================================
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
            counts = {str(row['contato_id']): row['nao_vistas'] for row in resultado}
            return jsonify({'success': True, 'counts': counts})
        return jsonify({'success': False, 'error': 'Erro na conexão com o banco de dados.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
# =============================================================
#  MOSTRAR ULTIMA MSG MA LISTA DE CONTATOS
# =============================================================
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
            for contato in contatos:
                contato['ultima_hora'] = contato['ultima_hora'].strftime('%H:%M') if contato['ultima_hora'] else ""
            return jsonify({'success': True, 'contatos': contatos})
        return jsonify({'success': False, 'error': 'Erro na conexão com o banco de dados.'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
# =============================================================
#  SE O USER ESTA ONLINE, OFF, AUSENTE
# =============================================================
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
                    return jsonify({'online': False}) 
                ultima_atividade = user['ultima_atividade']
                agora = datetime.now()
                online = (agora - ultima_atividade) < timedelta(seconds=60)
                return jsonify({'online': online})
        return jsonify({'online': False})
    except Exception as e:
        return jsonify({'online': False, 'error': str(e)})
# =============================================================
#  SE AS MENSAGENS FORAM VISTA
# =============================================================
@chat_bp.route('/api/status_visto/<int:destinatario_id>')
def status_visto(destinatario_id):
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'error': 'Usuário não autenticado'})
    usuario_id = session['usuario_id']
    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:

                # APENAS AS MSG ENVIADA PARA O DESTINATARIO
                cursor.execute("""
                    SELECT id, data_visualizacao
                    FROM mensagens
                    WHERE id_remetente = %s AND id_destinatario = %s
                """, (usuario_id, destinatario_id))
                msgs = cursor.fetchall()
            conexao.close()
            status = {str(m['id']): bool(m['data_visualizacao']) for m in msgs}
            return jsonify({'success': True, 'status': status})
        return jsonify({'success': False})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})