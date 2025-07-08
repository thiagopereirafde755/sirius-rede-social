import os
from flask import Blueprint, render_template, redirect, url_for, session, request, flash, Request
from werkzeug.utils import secure_filename
from app.conexao import criar_conexao
from app.utils import replace_mentions, formatar_data, replace_hashtags
from flask import jsonify
from datetime import datetime
import pickle

visualizacao_bp = Blueprint('vizualizacao', __name__)

@visualizacao_bp.route('/marcar_visualizacao', methods=['POST'])
def marcar_visualizacao():
    if 'usuario_id' not in session:
        return '', 401

    post_id = request.json.get('post_id')
    usuario_id = session['usuario_id']

    try:
        conexao = criar_conexao()
        with conexao.cursor() as cursor:
            cursor.execute("""
                INSERT IGNORE INTO visualizacoes (usuario_id, post_id)
                VALUES (%s, %s)
            """, (usuario_id, post_id))
        conexao.commit()
        conexao.close()
        return '', 204
    except Exception as e:
        return str(e), 500
