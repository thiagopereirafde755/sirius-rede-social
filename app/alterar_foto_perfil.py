import os
import base64
from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from werkzeug.utils import secure_filename
from app.conexao import criar_conexao
from datetime import datetime

alterar_foto_perfil_bp = Blueprint('foto', __name__)

UPLOAD_FOLDER_FOTO_PERFIL = 'static/img/uploads/foto_perfil'

@alterar_foto_perfil_bp.route('/alterar_foto_perfil', methods=['POST'])
def alterar_foto_perfil():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    # 1. Verifica se foi enviada uma imagem recortada
    if 'cropped_image' in request.form and request.form['cropped_image']:
        try:
            cropped_image = request.form['cropped_image']
            header, data = cropped_image.split(',', 1)
            file_ext = header.split('/')[1].split(';')[0]
            
            filename = f"perfil_{usuario_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_ext}"
            caminho_arquivo_absoluto = os.path.join(UPLOAD_FOLDER_FOTO_PERFIL, filename)
            caminho_arquivo_para_html = f"../static/img/uploads/foto_perfil/{filename}"
            
            os.makedirs(UPLOAD_FOLDER_FOTO_PERFIL, exist_ok=True)
            
            with open(caminho_arquivo_absoluto, 'wb') as f:
                f.write(base64.b64decode(data))
            
            conexao = criar_conexao()
            if conexao:
                cursor = conexao.cursor()
                cursor.execute("UPDATE users SET fotos_perfil = %s WHERE id = %s", (caminho_arquivo_para_html, usuario_id))
                conexao.commit()
                cursor.close()
                conexao.close()

            flash('Foto de perfil atualizada com sucesso!', 'success')
            return redirect(url_for('inicio.inicio'))
            
        except Exception as e:
            flash(f"Erro ao salvar a foto de perfil: {str(e)}", 'error')
            return redirect(url_for('inicio.inicio'))

    # 2. Verifica remoção da foto
    # 2. Verifica remoção da foto
    if 'remover_foto_perfil' in request.form:
        try:
            conexao = criar_conexao()
            if conexao:
                cursor = conexao.cursor()
                cursor.execute("UPDATE users SET fotos_perfil = NULL WHERE id = %s", (usuario_id,))
                conexao.commit()
                cursor.close()
                conexao.close()

            flash('Foto de perfil removida com sucesso.', 'success')
            return redirect(url_for('inicio.inicio'))
        except Exception as e:
            flash(f"Erro ao remover a foto de perfil: {str(e)}", 'error')
            return redirect(url_for('inicio.inicio'))

    # 3. Processamento tradicional (fallback)
    if 'nova_foto_perfil' not in request.files:
        flash('Nenhuma imagem foi enviada.', 'error')
        return redirect(url_for('inicio.inicio'))

    nova_foto_perfil = request.files['nova_foto_perfil']

    if nova_foto_perfil.filename == '':
        flash('Nenhuma imagem foi selecionada.', 'error')
        return redirect(url_for('inicio.inicio'))

    if nova_foto_perfil:
        filename = secure_filename(nova_foto_perfil.filename)
        caminho_arquivo_absoluto = os.path.join(UPLOAD_FOLDER_FOTO_PERFIL, filename)
        caminho_arquivo_para_html = f"../static/img/uploads/foto_perfil/{filename}"  
        try:
            os.makedirs(UPLOAD_FOLDER_FOTO_PERFIL, exist_ok=True)
            nova_foto_perfil.save(caminho_arquivo_absoluto)

            conexao = criar_conexao()
            if conexao:
                cursor = conexao.cursor()
                cursor.execute("UPDATE users SET fotos_perfil = %s WHERE id = %s", (caminho_arquivo_para_html, usuario_id))
                conexao.commit()
                cursor.close()
                conexao.close()

            flash('Foto de perfil atualizada com sucesso!', 'success')
        except Exception as e:
            flash(f"Erro ao salvar a foto de perfil: {str(e)}", 'error')
    
    return redirect(url_for('inicio.inicio'))