from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from werkzeug.utils import secure_filename
from app.conexao import criar_conexao


alterauser_bp = Blueprint('user', __name__)
@alterauser_bp.route('/alterar_user', methods=['POST'])
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