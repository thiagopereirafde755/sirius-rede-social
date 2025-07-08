import os
from flask import Blueprint, render_template, redirect, url_for, session, request, flash, jsonify
from werkzeug.utils import secure_filename
from app.utils import replace_mentions, extrair_mencoes, replace_hashtags
from app.conexao import criar_conexao
from datetime import datetime
from markupsafe import Markup
import re

postagem_bp = Blueprint('postagem', __name__)

@postagem_bp.app_template_filter('replace_hashtags')
def _replace_hashtags(text):
    return replace_hashtags(text)

@postagem_bp.app_template_filter('replace_mentions')
def _replace_mentions(text):
    return replace_mentions(text)

UPLOAD_FOLDER_VIDEOS = 'static/img/uploads/posts/video'
UPLOAD_FOLDER_FOTOS =  'static/img/uploads/posts/foto'

def extrair_hashtags(texto):
    """Extrai hashtags do texto."""
    return set(re.findall(r'#\w+', texto or ""))

@postagem_bp.route('/adicionar_postagem', methods=['POST'])
def adicionar_postagem():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))
    
    usuario_id = session['usuario_id']
    conteudo = request.form.get('conteudo')
    
    if not conteudo:
        flash('O conteúdo da postagem não pode estar vazio.')
        return redirect(url_for('inicio.inicio'))

    # Processando a imagem, se enviada
    imagem = request.files.get('imagem')
    imagem_caminho = None
    if imagem and imagem.filename != '':
        imagem_filename = secure_filename(imagem.filename)
        imagem_filename = imagem_filename.replace("\\", "/")
        caminho_imagem_absoluto = os.path.join(UPLOAD_FOLDER_FOTOS, imagem_filename)
        imagem.save(caminho_imagem_absoluto)
        imagem_caminho = f"../static/img/uploads/posts/foto/{imagem_filename}"

    # Processando o vídeo, se enviado
    video = request.files.get('video')
    video_caminho = None
    if video and video.filename != '':
        video_filename = secure_filename(video.filename)
        video_filename = video_filename.replace("\\", "/")
        caminho_video_absoluto = os.path.join(UPLOAD_FOLDER_VIDEOS, video_filename)
        video.save(caminho_video_absoluto)
        video_caminho = f"../static/img/uploads/posts/video/{video_filename}"

    try:
        conexao = criar_conexao()
        if conexao:
            cursor = conexao.cursor()

            # Inserindo o post no banco de dados
            cursor.execute("""
                INSERT INTO posts (users_id, conteudo, imagem, video) 
                VALUES (%s, %s, %s, %s)
            """, (usuario_id, conteudo, imagem_caminho, video_caminho))
            conexao.commit()
            post_id = cursor.lastrowid

            # Extrair e salvar hashtags
            hashtags = extrair_hashtags(conteudo)
            for hashtag in hashtags:
                # Insere a hashtag se não existir
                cursor.execute("INSERT IGNORE INTO hashtags (nome) VALUES (%s)", (hashtag,))
                # Obtém o id da hashtag
                cursor.execute("SELECT id FROM hashtags WHERE nome = %s", (hashtag,))
                hashtag_id = cursor.fetchone()[0]
                # Relaciona o post à hashtag
                cursor.execute(
                    "INSERT IGNORE INTO post_hashtags (post_id, hashtag_id) VALUES (%s, %s)",
                    (post_id, hashtag_id)
                )
            conexao.commit()

            # Extrair menções e criar notificações
            mencoes = extrair_mencoes(conteudo)
            for username in mencoes:
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                resultado = cursor.fetchone()
                if resultado:
                    mencionado_id = resultado[0]
                    cursor.execute("""
                        INSERT INTO notificacoes (usuario_id, tipo, origem_usuario_id, post_id, lida)
                        VALUES (%s, 'mencao', %s, %s, 0)
                    """, (mencionado_id, usuario_id, post_id))
            conexao.commit()

            cursor.close()
            conexao.close()

            flash('Postagem realizada com sucesso!')
    except Exception as e:
        flash(f"Erro ao adicionar a postagem: {str(e)}")

    return redirect(url_for('inicio.inicio'))

@postagem_bp.route('/autocomplete_hashtags')
def autocomplete_hashtags():
    termo = request.args.get('q', '').strip().lower()
    if not termo or not termo.startswith('#'):
        return jsonify([])  # não faz nada se não começar com #
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
        return jsonify([])  # em produção, logue o erro