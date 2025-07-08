import os
import base64
from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from werkzeug.utils import secure_filename
from app.conexao import criar_conexao
from datetime import datetime

alterar_capa_bp = Blueprint('capa', __name__)

# Configuração do diretório de upload
UPLOAD_FOLDER_CAPA = 'static/img/uploads/capa'

@alterar_capa_bp.route('/alterar_capa', methods=['POST'])
def alterar_capa():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    # 1. Verifica se foi enviada uma imagem recortada (via Cropper.js)
    if 'cropped_image' in request.form and request.form['cropped_image']:
        try:
            cropped_image = request.form['cropped_image']
            
            # Remove o prefixo da string base64
            header, data = cropped_image.split(',', 1)
            
            # Obtém a extensão do arquivo (jpeg, png, etc.)
            file_ext = header.split('/')[1].split(';')[0]
            
            # Gera um nome de arquivo único
            filename = f"capa_{usuario_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_ext}"
            caminho_arquivo_absoluto = os.path.join(UPLOAD_FOLDER_CAPA, filename)
            caminho_arquivo_para_html = f"../static/img/uploads/capa/{filename}"
            
            # Garante que o diretório de upload existe
            os.makedirs(UPLOAD_FOLDER_CAPA, exist_ok=True)
            
            # Salva a imagem recortada
            with open(caminho_arquivo_absoluto, 'wb') as f:
                f.write(base64.b64decode(data))
            
            # Atualiza no banco de dados
            conexao = criar_conexao()
            if conexao:
                cursor = conexao.cursor()
                cursor.execute("UPDATE users SET foto_capa = %s WHERE id = %s", (caminho_arquivo_para_html, usuario_id))
                conexao.commit()
                cursor.close()
                conexao.close()

            flash('Foto de capa atualizada com sucesso!', 'success')
            return redirect(url_for('inicio.inicio'))
            
        except Exception as e:
            flash(f"Erro ao salvar a foto de capa: {str(e)}", 'error')
            return redirect(url_for('inicio.inicio'))

    # 2. Verifica se o botão de remover foto de capa foi pressionado
# 2. Verifica se o botão de remover foto de capa foi pressionado
    if 'remover_foto_capa' in request.form:
        try:
            conexao = criar_conexao()
            if conexao:
                cursor = conexao.cursor()
                cursor.execute("UPDATE users SET foto_capa = NULL WHERE id = %s", (usuario_id,))
                conexao.commit()
                cursor.close()
                conexao.close()

            flash('Foto de capa removida com sucesso.', 'success')
            return redirect(url_for('inicio.inicio'))
        except Exception as e:
            flash(f"Erro ao remover a foto de capa: {str(e)}", 'error')
            return redirect(url_for('inicio.inicio'))

    # 3. Processamento tradicional de upload de arquivo (fallback)
    if 'nova_capa' not in request.files:
        flash('Nenhuma imagem foi enviada.', 'error')
        return redirect(url_for('inicio.inicio'))

    nova_capa = request.files['nova_capa']

    if nova_capa.filename == '':
        flash('Nenhuma imagem foi selecionada.', 'error')
        return redirect(url_for('inicio.inicio'))

    if nova_capa:
        filename = secure_filename(nova_capa.filename)
        caminho_arquivo_absoluto = os.path.join(UPLOAD_FOLDER_CAPA, filename)
        caminho_arquivo_para_html = f"../static/img/uploads/capa/{filename}"  
        
        try:
            # Garante que o diretório de upload existe
            os.makedirs(UPLOAD_FOLDER_CAPA, exist_ok=True)
            
            # Salva o arquivo
            nova_capa.save(caminho_arquivo_absoluto)

            # Atualiza no banco de dados
            conexao = criar_conexao()
            if conexao:
                cursor = conexao.cursor()
                cursor.execute("UPDATE users SET foto_capa = %s WHERE id = %s", (caminho_arquivo_para_html, usuario_id))
                conexao.commit()
                cursor.close()
                conexao.close()

            flash('Foto de capa atualizada com sucesso!', 'success')
        except Exception as e:
            flash(f"Erro ao salvar a foto de capa: {str(e)}", 'error')
    
    return redirect(url_for('inicio.inicio'))