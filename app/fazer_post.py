from flask import Blueprint, request, redirect, url_for, flash, session, jsonify
import os
import cloudinary
import cloudinary.uploader
from app.conexao import criar_conexao
from app.utils import extrair_hashtags, extrair_mencoes
from dotenv import load_dotenv
import traceback

# =============================================================
#  CONFIGURAÇAO DA CLOUDINARY
# =============================================================
load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

postagem_bp = Blueprint('postagem', __name__)

# =============================================================
#  FAZER POST
# =============================================================
@postagem_bp.route('/adicionar_postagem', methods=['POST'])
def adicionar_postagem():
    if 'usuario_id' not in session:
        flash("Você precisa estar logado para postar.")
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']
    conteudo = request.form.get('conteudo')

    print(f"[LOG] Usuário {usuario_id} criando postagem com conteúdo: {conteudo}")

    if not conteudo or conteudo.strip() == '':
        flash('O conteúdo da postagem não pode estar vazio.')
        return redirect(url_for('inicio.inicio'))

    imagem = request.files.get('imagem')
    video = request.files.get('video')

    imagem_caminho = None
    video_caminho = None
    imagem_public_id = None
    video_public_id = None

    # IMAGEM
    if imagem and imagem.filename != '':
        print(f"[LOG] Recebida imagem: {imagem.filename}")
        try:
            resultado_upload_img = cloudinary.uploader.upload(
                imagem,
                folder='posts/fotos'
            )
            imagem_caminho = resultado_upload_img.get('secure_url')
            imagem_public_id = resultado_upload_img.get('public_id')
            print(f"[LOG] Upload imagem concluído: {imagem_caminho}")
        except Exception as e:
            print("[ERRO] Upload da imagem falhou:")
            traceback.print_exc()
            flash(f"Erro ao enviar imagem: {str(e)}")
            return redirect(url_for('inicio.inicio'))

    # VIDEO
    if video and video.filename != '':
        print(f"[LOG] Recebido vídeo: {video.filename}")
        try:
            resultado_upload_vid = cloudinary.uploader.upload(
                video,
                resource_type='video',
                folder='posts/videos'
            )
            video_caminho = resultado_upload_vid.get('secure_url')
            video_public_id = resultado_upload_vid.get('public_id')
            print(f"[LOG] Upload vídeo concluído: {video_caminho}")
        except Exception as e:
            print("[ERRO] Upload do vídeo falhou:")
            traceback.print_exc()
            flash(f"Erro ao enviar vídeo: {str(e)}")
            return redirect(url_for('inicio.inicio'))

    try:
        conexao = criar_conexao()
        if not conexao:
            flash("Erro na conexão com o banco de dados.")
            return redirect(url_for('inicio.inicio'))

        cursor = conexao.cursor()

        cursor.execute("""
            INSERT INTO posts (users_id, conteudo, imagem, video, imagem_public_id, video_public_id) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (usuario_id, conteudo, imagem_caminho, video_caminho, imagem_public_id, video_public_id))

        conexao.commit()
        post_id = cursor.lastrowid

        # SALVA AS HASHTAGS
        hashtags = extrair_hashtags(conteudo)
        for hashtag in hashtags:
            cursor.execute("INSERT IGNORE INTO hashtags (nome) VALUES (%s)", (hashtag,))
            cursor.execute("SELECT id FROM hashtags WHERE nome = %s", (hashtag,))
            hashtag_id = cursor.fetchone()[0]
            cursor.execute("INSERT IGNORE INTO post_hashtags (post_id, hashtag_id) VALUES (%s, %s)", (post_id, hashtag_id))

        # SALVA AS MENÇÕES
        mencoes = extrair_mencoes(conteudo)
        for username in mencoes:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            resultado = cursor.fetchone()
            if resultado:
                mencionado_id = resultado[0]
                cursor.execute("INSERT INTO post_mencoes (post_id, user_mencionado_id) VALUES (%s, %s)", (post_id, mencionado_id))
                cursor.execute("""
                    INSERT INTO notificacoes (usuario_id, tipo, origem_usuario_id, post_id, lida)
                    VALUES (%s, 'mencao', %s, %s, 0)
                """, (mencionado_id, usuario_id, post_id))

        conexao.commit()
        cursor.close()
        conexao.close()

        flash('Postagem realizada com sucesso!')
        return redirect(url_for('inicio.inicio'))

    except Exception as e:
        print("[ERRO] Erro ao adicionar a postagem:")
        traceback.print_exc()
        flash(f"Erro ao adicionar a postagem: {str(e)}")
        return redirect(url_for('inicio.inicio'))
# =============================================================
#  AUTOCOMPLETE DE HASHTAGS
# =============================================================
@postagem_bp.route('/autocomplete_hashtags')
def autocomplete_hashtags():
    termo = request.args.get('q', '').strip().lower()
    if not termo or not termo.startswith('#'):
        return jsonify([])  
    try:
        conexao = criar_conexao()
        with conexao.cursor(dictionary=True) as cursor:
            cursor.execute("""
                SELECT h.nome, COUNT(ph.post_id) as total
                FROM hashtags h
                LEFT JOIN post_hashtags ph ON h.id = ph.hashtag_id
                WHERE h.nome LIKE %s
                GROUP BY h.nome
                ORDER BY total DESC, h.nome ASC
                LIMIT 10
            """, (termo+'%',))
            resultados = cursor.fetchall()
        conexao.close()
        return jsonify(resultados)
    except Exception as e:
        return jsonify([]) 