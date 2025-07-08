from flask import Flask, render_template, session, request, redirect
import os
from app.conexao import criar_conexao
from datetime import datetime, timedelta
import secrets

from app import (
    cadastrar,
    login,
    inicio,
    log_out,
    home,
    info_user,
    posts_seguindo,
    chat,
    comentar,
    curtir,
    alterar_bio,
    alterar_nome,
    alterar_user,
    alterar_foto_perfil,
    altera_capa_perfil,
    fazer_post,
    excluir_post,
    apagar_comentario,
    posts_curtido,
    posts_video,
    procurar_user,
    configuracao,
    notificacao,
    online,
    enviar_post_chat,
    seguir,
    mencao_comentario_post,
    recuperar_senha,
    vizualizar_post,
    confirmar_conta,
    recuperar_senha_nao_logado,

)

app = Flask(__name__)

app.secret_key = secrets.token_hex(32)

# Duração da sessão: 7 dias
app.permanent_session_lifetime = timedelta(days=7)

app.config.update(
    SESSION_COOKIE_SAMESITE='Lax',
    SESSION_COOKIE_SECURE=False
)

blueprints = [
    cadastrar.cadastrar_bp,
    login.login_bp,
    inicio.inicio_bp,
    log_out.logout_bp,
    home.home_bp,
    info_user.info_bp,
    posts_seguindo.posteseguindo_bp,
    chat.chat_bp,
    comentar.comentar_bp,
    curtir.curtir_bp,
    alterar_bio.bio_bp,
    alterar_nome.alteranome_bp,
    alterar_user.alterauser_bp,
    alterar_foto_perfil.alterar_foto_perfil_bp,
    altera_capa_perfil.alterar_capa_bp,
    fazer_post.postagem_bp,
    excluir_post.excluir_post_bp,
    apagar_comentario.apagar_comentario_bp,
    posts_video.postesvideo_bp,
    posts_curtido.curtidas_post_bp,
    procurar_user.prucura_user_bp,
    configuracao.configuracao_bp,
    notificacao.notificacao_bp,
    online.online_bp,
    enviar_post_chat.enviar_post_chat_bp,
    seguir.seguir_bp,
    mencao_comentario_post.mencao_comentario_post_bp,
    recuperar_senha.recuperar_senha_logado_bp,
    vizualizar_post.visualizacao_bp,
    confirmar_conta.confirmar_bp,
    recuperar_senha_nao_logado.recuperar_senha_bp,
]

for bp in blueprints:
    app.register_blueprint(bp)

@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect('/inicio')
    return render_template('index.html')

@app.route('/cadastro')
def cadastro():
    return render_template('cadastro.html')

@app.route('/inicio')
def pag_inicio():
    return render_template('pagina-incial.html')

@app.route('/comentarios_count/<int:post_id>')
def comentarios_count(post_id):
    conexao = criar_conexao()
    with conexao.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM comentarios WHERE post_id = %s", (post_id,))
        count = cursor.fetchone()[0]
    conexao.close()
    return {'count': count}

if __name__ == '__main__':
    app.run(debug=True)
