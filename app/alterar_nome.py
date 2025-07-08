from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from werkzeug.utils import secure_filename
from app.conexao import criar_conexao


alteranome_bp = Blueprint('nome', __name__)

@alteranome_bp.route('/alterar_nome', methods=['POST'])
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