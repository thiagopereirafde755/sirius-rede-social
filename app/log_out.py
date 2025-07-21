from flask import Blueprint, redirect, url_for, session, request
from app.conexao import criar_conexao

logout_bp = Blueprint('logout', __name__)

# =============================================================
#  PARA SAIR DA CONTA
# =============================================================
@logout_bp.route('/logout')
def logout():
    usuario_id = session.get('usuario_id')
    token_sessao = session.get('token_sessao') 

    if usuario_id and token_sessao:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:

                # Marca usuário como offline
                cursor.execute("UPDATE users SET online = 0 WHERE id = %s", (usuario_id,))
                
                # Remove o dispositivo atual da tabela
                cursor.execute("""
                    DELETE FROM usuarios_dispositivos
                    WHERE usuario_id = %s AND token_sessao = %s
                """, (usuario_id, token_sessao))

                conexao.commit()
            conexao.close()

    session.pop('usuario_id', None)
    session.pop('token_sessao', None) 
    return redirect(url_for('index'))
