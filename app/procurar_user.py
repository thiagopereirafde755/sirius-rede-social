from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from werkzeug.utils import secure_filename
from app.conexao import criar_conexao
from datetime import datetime

prucura_user_bp = Blueprint('procurar_user', __name__)

@prucura_user_bp.route('/procurar-user')
def inicio():
    if 'usuario_id' not in session:
        return redirect(url_for('index'))

    usuario_id = session['usuario_id']
    query = request.args.get('query', '')

    try:
        conexao = criar_conexao()

        if conexao:
            with conexao.cursor(dictionary=True) as cursor:
                # Informações do usuário
                cursor.execute("SELECT fotos_perfil, username, tema FROM users WHERE id = %s", (usuario_id,))
                usuario = cursor.fetchone()

                # Informações do perfil do usuário
                if usuario:
                    tema = usuario.get('tema', 'claro')  # agora funciona
                    nome_usuario=usuario['username']
                    foto_perfil = usuario['fotos_perfil'] if usuario['fotos_perfil'] else url_for('static', filename='img/icone/user.png')
                else:
                    foto_perfil = url_for('static', filename='img/icone/user.png')
                    tema = 'tema'

                           # Buscar as 3 hashtags mais usadas nas últimas 10 horas
                cursor.execute("""
                    SELECT h.nome, COUNT(*) as total
                    FROM hashtags h
                    JOIN post_hashtags ph ON h.id = ph.hashtag_id
                    JOIN posts p ON ph.post_id = p.id
                    WHERE p.data_postagem >= NOW() - INTERVAL 10 HOUR
                    GROUP BY h.id, h.nome
                    ORDER BY total DESC
                    LIMIT 3
                """)
                hashtags_top = cursor.fetchall()

                # Pesquisar usuários
                if query:
                    cursor.execute("SELECT id, username, fotos_perfil FROM users WHERE username LIKE %s", (f"%{query}%",))
                    resultados = cursor.fetchall()
                else:
                    resultados = []

                conexao.close()

            return render_template('procurar-user.html', usuario_id=usuario_id, 
                                   foto_perfil=foto_perfil, 
                                   resultados=resultados, 
                                   query=query, 
                                   nome_usuario=nome_usuario,
                                   tema=tema,
                                    hashtags_top=hashtags_top, )
        
        return "Erro na conexão com o banco de dados."

    except Exception as e:
        return f"Erro ao conectar ao banco de dados: {str(e)}"