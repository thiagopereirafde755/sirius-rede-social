from flask import Blueprint, redirect, url_for, session
from app.conexao import criar_conexao

logout_bp = Blueprint('logout', __name__)

@logout_bp.route('/logout')
def logout():
    usuario_id = session.get('usuario_id')
    if usuario_id:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
                cursor.execute("UPDATE users SET online = 0 WHERE id = %s", (usuario_id,))
                conexao.commit()
            conexao.close()
    session.pop('usuario_id', None)
    return redirect(url_for('index'))