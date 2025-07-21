from flask import Blueprint, render_template

central_de_ajuda_bp = Blueprint('central_ajuda', __name__)

# =============================================================
#  PARA REDERIZAR O HTML DE CENTRAL DE AJUDA E INFORMAÇÕES
# =============================================================
@central_de_ajuda_bp.route('/central_ajuda')
def central_de_ajuda1():
    return render_template('central_de_ajuda.html')

@central_de_ajuda_bp.route('/central_ajuda/como_criar_conta')
def como_criar_conta():
    return render_template('central_de_ajuda_como_criar_conta.html')

@central_de_ajuda_bp.route('/central_ajuda/problemas_com_login')
def problemas_com_login():
    return render_template('central_de_ajuda_problemas_login.html')

@central_de_ajuda_bp.route('/central_ajuda/comentarios_de_post')
def comentarios_de_post():
    return render_template('central_de_ajuda_comentarios_de_post.html')

@central_de_ajuda_bp.route('/central_ajuda/suporte')
def suporte():
    return render_template('central_de_ajuda_suporte.html')

@central_de_ajuda_bp.route('/central_ajuda/recuperar_senha')
def recuperar_senha():
    return render_template('central_de_ajuda_recuperar_senha.html')

@central_de_ajuda_bp.route('/central_ajuda/configuracao')
def configuracao():
    return render_template('central_de_ajuda_configuracao.html')

@central_de_ajuda_bp.route('/central_ajuda/excluir_conta')
def configuracao_excluir_conta():
    return render_template('central_de_ajuda_excluir_conta.html')

@central_de_ajuda_bp.route('/central_ajuda/curtidas_de_post')
def curtidas_post():
    return render_template('central_de_ajuda_curtidas_post.html')

@central_de_ajuda_bp.route('/central_ajuda/salvo_post')
def salvo_post():
    return render_template('central_de_ajuda_salvo_post.html')

@central_de_ajuda_bp.route('/central_ajuda/republicar_de_post')
def republicar_post():
    return render_template('central_de_ajuda_republicar_post.html')

@central_de_ajuda_bp.route('/central_ajuda/fazer_post')
def fazer_post():
    return render_template('central_de_ajuda_fazer_post.html')

@central_de_ajuda_bp.route('/central_ajuda/seguranca_privacidade')
def seguranca_privacidade():
    return render_template('central_de_ajuda_seguranca_privacidade.html')

@central_de_ajuda_bp.route('/central_ajuda/seguidores_seguindo')
def segudores_seguindo():
    return render_template('central_de_ajuda_seguidores_seguindo.html')

@central_de_ajuda_bp.route('/central_ajuda/chat')
def chat():
    return render_template('central_de_ajuda_chat.html')

@central_de_ajuda_bp.route('/central_ajuda/notificacao')
def notificacao():
    return render_template('central_de_ajuda_notificacao.html')

@central_de_ajuda_bp.route('/central_ajuda/perfil_usuario')
def pef_user():
    return render_template('central_de_ajuda_perfil_usuario.html')

@central_de_ajuda_bp.route('/central_ajuda/suspensao')
def pef_suspensao():
    return render_template('central_de_ajuda_suspensao.html')

@central_de_ajuda_bp.route('/central_ajuda/amigos')
def pef_amigos():
    return render_template('central_de_ajuda_amigos.html')

@central_de_ajuda_bp.route('/central_ajuda/alterar_senha')
def alterar_senha():
    return render_template('central_de_ajuda_alterar_senha.html')

@central_de_ajuda_bp.route('/central_ajuda/denunciar_problemas')
def denunciar_problemas():
    return render_template('central_de_ajuda_denunciar_problemas.html')

@central_de_ajuda_bp.route('/termos-de-uso')
def termo_uso():
    return render_template('termo_de_uso.html')

@central_de_ajuda_bp.route('/politica-de-privacidade')
def politica_privacidade():
    return render_template('politica_de_privacidade.html')

@central_de_ajuda_bp.route('/cookies')
def cookies():
    return render_template('cookies.html')

@central_de_ajuda_bp.route('/sobre_nos')
def sobre_nos():
    return render_template('sobre_nos.html')