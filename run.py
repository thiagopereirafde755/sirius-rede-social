from flask import Flask, render_template, session, redirect
from app.conexao import criar_conexao
from datetime import  timedelta
import secrets

from app.utils import formatar_numero_curto


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
    administrador,
    denuncias,
    republicar_post,
    salvar_post,
    post_republicado,
    post_salvos,
    central_ajuda,
    editar_perfil,

)

app = Flask(__name__)

app.jinja_env.filters['numcurto'] = formatar_numero_curto

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
    administrador.administrador_bp,
    denuncias.denuncia_bp,
    republicar_post.republicar_bp,
    salvar_post.salvar_bp,
    post_republicado.republicado_post_bp,
    post_salvos.salvo_post_bp,
    central_ajuda.central_de_ajuda_bp,
    editar_perfil.editar_perfil_bp
]

for bp in blueprints:
    app.register_blueprint(bp)

@app.route('/')
def index():
    if 'usuario_id' in session:
        return redirect('/inicio')
    return render_template('index.html')

@app.route('/adm')
def pag_adm():
    return render_template('login_adm.html')

@app.route('/cadastro')
def cadastro():
    if 'usuario_id' in session:
        return redirect('/inicio')
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
