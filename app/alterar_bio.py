import os
from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from werkzeug.utils import secure_filename
from app.conexao import criar_conexao
from datetime import datetime

bio_bp = Blueprint('bio', __name__)

@bio_bp.route('/alterar_bio', methods=['POST'])
def alterar_bio():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']
    
    # Verifica se o botão de apagar bio foi pressionado
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