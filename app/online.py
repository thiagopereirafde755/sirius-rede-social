from flask import Blueprint, session, jsonify
from app.conexao import criar_conexao
from datetime import datetime, timedelta

online_bp = Blueprint('online', __name__)

# =============================================================
#  DEF PARA DEIXA OFF DPS DE 1 MINUTO
# =============================================================
def esta_online(ultima_atividade):
    return ultima_atividade > datetime.now() - timedelta(seconds=60)
# =============================================================
#  DEIXA ON
# =============================================================
@online_bp.route('/api/ping_online', methods=['POST'])
def ping_online():
    if 'usuario_id' not in session:
        return jsonify({'success': False})
    usuario_id = session['usuario_id']
    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
                cursor.execute("UPDATE users SET online = 1, ultima_atividade = NOW() WHERE id = %s", (usuario_id,))
                conexao.commit()
            conexao.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
# =============================================================
#  DEIXA OFF
# =============================================================
@online_bp.route('/api/set_offline', methods=['POST'])
def set_offline():
    if 'usuario_id' not in session:
        return jsonify({'success': False})
    usuario_id = session['usuario_id']
    try:
        conexao = criar_conexao()
        if conexao:
            with conexao.cursor() as cursor:
                cursor.execute("UPDATE users SET online = 0 WHERE id = %s", (usuario_id,))
                conexao.commit()
            conexao.close()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})
    
    