import os
import base64
from flask import Blueprint, redirect, url_for, session, request, flash
from werkzeug.utils import secure_filename
from app.conexao import criar_conexao
from datetime import datetime
import cloudinary.uploader
from dotenv import load_dotenv
import traceback
import cloudinary

editar_perfil_bp = Blueprint('editar_perfil', __name__)

# =============================================================
#  CONFIGURAÇAO DA CLOUDINARY
# =============================================================
load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)

# =============================================================
#  ALTERAR CAPA DE PERFIL
# =============================================================
@editar_perfil_bp.route('/alterar_capa', methods=['POST'])
def alterar_capa():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    # ============================ BASE64 (recorte JS)
    if 'cropped_image' in request.form and request.form['cropped_image']:
        try:
            cropped_image = request.form['cropped_image']
            header, data = cropped_image.split(',', 1)
            file_ext = header.split('/')[1].split(';')[0]
            file_data = base64.b64decode(data)

            # Upload para Cloudinary diretamente do binário
            result = cloudinary.uploader.upload(file_data,
                folder="capa_usuarios",
                public_id=f"capa_{usuario_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                resource_type="image"
            )
            url_capa = result['secure_url']

            # SALVA NO BANCO
            conexao = criar_conexao()
            cursor = conexao.cursor()
            cursor.execute("UPDATE users SET foto_capa = %s WHERE id = %s", (url_capa, usuario_id))
            conexao.commit()
            cursor.close()
            conexao.close()

            flash('Foto de capa atualizada com sucesso!', 'success')
            return redirect(url_for('inicio.inicio'))

        except Exception as e:
            flash(f"Erro ao salvar a foto de capa: {str(e)}", 'error')
            return redirect(url_for('inicio.inicio'))

    # ============================ REMOÇÃO
    if 'remover_foto_capa' in request.form:
        try:
            conexao = criar_conexao()
            cursor = conexao.cursor()
            cursor.execute("UPDATE users SET foto_capa = NULL WHERE id = %s", (usuario_id,))
            conexao.commit()
            cursor.close()
            conexao.close()
            flash('Foto de capa removida com sucesso.', 'success')
        except Exception as e:
            flash(f"Erro ao remover a foto de capa: {str(e)}", 'error')

        return redirect(url_for('inicio.inicio'))

    # ============================ UPLOAD DIRETO (arquivo)
    if 'nova_capa' not in request.files:
        flash('Nenhuma imagem foi enviada.', 'error')
        return redirect(url_for('inicio.inicio'))

    nova_capa = request.files['nova_capa']
    if nova_capa.filename == '':
        flash('Nenhuma imagem foi selecionada.', 'error')
        return redirect(url_for('inicio.inicio'))

    if nova_capa:
        try:
            # Upload para Cloudinary
            result = cloudinary.uploader.upload(nova_capa,
                folder="capa_usuarios",
                public_id=f"capa_{usuario_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                resource_type="image"
            )
            url_capa = result['secure_url']

            # SALVA NO BD
            conexao = criar_conexao()
            cursor = conexao.cursor()
            cursor.execute("UPDATE users SET foto_capa = %s WHERE id = %s", (url_capa, usuario_id))
            conexao.commit()
            cursor.close()
            conexao.close()

            flash('Foto de capa atualizada com sucesso!', 'success')
        except Exception as e:
            flash(f"Erro ao salvar a foto de capa: {str(e)}", 'error')

    return redirect(url_for('inicio.inicio'))
# =============================================================
#  ALTERAR FOTO DE PERFIL
# =============================================================

# PASTA CLOUDINARY
PASTA_CLOUDINARY_PERFIL = "foto_perfil"

@editar_perfil_bp.route('/alterar_foto_perfil', methods=['POST'])
def alterar_foto_perfil():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']

    # ================================
    # 1. FOTO CORTADA (base64)
    # ================================
    if 'cropped_image' in request.form and request.form['cropped_image']:
        try:
            cropped_image = request.form['cropped_image']
            header, data = cropped_image.split(',', 1)
            file_ext = header.split('/')[1].split(';')[0]
            nome_arquivo = f"perfil_{usuario_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.{file_ext}"
            
            result = cloudinary.uploader.upload(
                base64.b64decode(data),
                folder=PASTA_CLOUDINARY_PERFIL,
                public_id=nome_arquivo.rsplit('.', 1)[0],
                resource_type='image'
            )
            url_final = result['secure_url']

            conexao = criar_conexao()
            if conexao:
                cursor = conexao.cursor()
                cursor.execute("UPDATE users SET fotos_perfil = %s WHERE id = %s", (url_final, usuario_id))
                conexao.commit()
                cursor.close()
                conexao.close()

            flash('Foto de perfil atualizada com sucesso!', 'success')
            return redirect(url_for('inicio.inicio'))

        except Exception as e:
            flash(f"Erro ao salvar a foto de perfil: {str(e)}", 'error')
            return redirect(url_for('inicio.inicio'))

    # ================================
    # 2. REMOVER FOTO
    # ================================
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

    # ================================
    # 3. UPLOAD DE ARQUIVO DIRETO
    # ================================
    if 'nova_foto_perfil' not in request.files:
        flash('Nenhuma imagem foi enviada.', 'error')
        return redirect(url_for('inicio.inicio'))

    nova_foto_perfil = request.files['nova_foto_perfil']

    if nova_foto_perfil.filename == '':
        flash('Nenhuma imagem foi selecionada.', 'error')
        return redirect(url_for('inicio.inicio'))

    try:
        filename = secure_filename(nova_foto_perfil.filename)
        nome_arquivo = f"perfil_{usuario_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        result = cloudinary.uploader.upload(
            nova_foto_perfil,
            folder=PASTA_CLOUDINARY_PERFIL,
            public_id=nome_arquivo,
            resource_type='image'
        )
        url_final = result['secure_url']

        conexao = criar_conexao()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("UPDATE users SET fotos_perfil = %s WHERE id = %s", (url_final, usuario_id))
            conexao.commit()
            cursor.close()
            conexao.close()

        flash('Foto de perfil atualizada com sucesso!', 'success')

    except Exception as e:
        flash(f"Erro ao salvar a foto de perfil: {str(e)}", 'error')

    return redirect(url_for('inicio.inicio'))
# =============================================================
#  ALTERAR BIO
# =============================================================
@editar_perfil_bp.route('/alterar_bio', methods=['POST'])
def alterar_bio():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']
    
    apagar_bio = 'apagar_bio' in request.form
    nova_bio = '' if apagar_bio else request.form.get('nova_bio', '').strip()

    try:
        conexao = criar_conexao()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("UPDATE users SET bio = %s WHERE id = %s", (nova_bio, usuario_id))
            conexao.commit()
            cursor.close()
            conexao.close()

            if apagar_bio:
                flash('Bio apagada com sucesso!', 'success')
            elif nova_bio:
                flash('Bio atualizada com sucesso!', 'success')
            else:
                flash('Nenhuma alteração realizada.', 'info')

            return redirect(url_for('inicio.inicio'))

    except Exception as e:
        flash(f"Erro ao atualizar a bio: {str(e)}", 'error')
        return redirect(url_for('inicio.inicio'))
# =============================================================
#  ALTERAR NOME
# =============================================================  
@editar_perfil_bp.route('/alterar_nome', methods=['POST'])
def alterar_nome():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']
    

    novo_nome = request.form.get('novo_nome')
    
    if not novo_nome:
        flash('o nome não pode estar vazia.')
        return redirect(url_for('inicio.inicio'))

    try:
        conexao = criar_conexao()
        if conexao:
            cursor = conexao.cursor()
            cursor.execute("UPDATE users SET nome = %s WHERE id = %s", (novo_nome, usuario_id))
            conexao.commit()
            cursor.close()
            conexao.close()

            flash('nome atualizada com sucesso.')
    except Exception as e:
        flash(f"Erro ao atualizar o nome: {str(e)}")
    
    return redirect(url_for('inicio.inicio'))
# =============================================================
#  ALTERAR USERNAME
# =============================================================
@editar_perfil_bp.route('/alterar_user', methods=['POST'])
def alterar_user():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']
    novo_user = request.form.get('novo_user')

    if not novo_user:
        flash('O username não pode estar vazio.')
        return redirect(url_for('inicio.inicio'))

    try:
        conexao = criar_conexao()
        if conexao:
            cursor = conexao.cursor()

            cursor.execute("SELECT id FROM users WHERE username = %s", (novo_user,))
            resultado = cursor.fetchone()
            if resultado and resultado[0] != usuario_id:
                flash('Este username já está em uso. Por favor, escolha outro.')
                cursor.close()
                conexao.close()
                return redirect(url_for('inicio.inicio'))

            cursor.execute("UPDATE users SET username = %s WHERE id = %s", (novo_user, usuario_id))
            conexao.commit()

            flash('Usuário atualizado com sucesso.')
            cursor.close()
            conexao.close()

    except Exception as e:
        flash(f"Erro ao atualizar o usuário: {str(e)}")
    
    return redirect(url_for('inicio.inicio'))