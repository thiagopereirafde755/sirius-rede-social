from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from werkzeug.utils import secure_filename
from app.conexao import criar_conexao
from datetime import datetime
from flask import request

excluir_post_bp = Blueprint('excluirpost', __name__)


@excluir_post_bp.route('/excluir_post_inicio/<int:post_id>', methods=['POST'])
def excluir_post(post_id):
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    next_page = request.form.get('next')
    usuario_id = session['usuario_id']
    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT users_id FROM posts WHERE id = %s", (post_id,))
                post = cursor.fetchone()
                if post and post['users_id'] == usuario_id:
                    cursor.execute("DELETE FROM notificacoes WHERE post_id = %s", (post_id,))
                    cursor.execute("DELETE FROM comentarios WHERE post_id = %s", (post_id,))
                    cursor.execute("DELETE FROM curtidas WHERE post_id = %s", (post_id,))
                    cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
                    conexao.commit()
                    flash('Post excluído com sucesso.', 'success')
                else:
                    flash('Você não tem permissão para excluir este post.', 'danger')
            conexao.close()
        return redirect(next_page or url_for('inicio.inicio'))
    except Exception as e:
        flash(f'Erro ao excluir o post: {str(e)}', 'danger')
        return redirect(next_page or url_for('inicio.inicio'))
    
