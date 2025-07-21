from flask import Blueprint, session, request, jsonify
from app.conexao import criar_conexao
from datetime import datetime
from flask import request

denuncia_bp = Blueprint('denuncia', __name__)

# =============================================================
#  DENUNCIAR POST
# =============================================================
@denuncia_bp.route('/api/denunciar', methods=['POST'])
def denunciar_post():

    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return jsonify(success=False,
                       message='Você precisa estar logado para denunciar.'), 401

    post_id  = request.form.get('post_id',  type=int)
    motivo   = request.form.get('motivo',   '').strip()
    detalhes = request.form.get('detalhes', '').strip()

    if not post_id or not motivo:
        return jsonify(success=False,
                       message='Motivo da denúncia é obrigatório.'), 400

    conn = criar_conexao()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO denuncias (tipo, id_alvo, id_denunciante,
                                       motivo, descricao, data_denuncia)
                VALUES ('post', %s, %s, %s, %s, %s)
            """, (post_id, usuario_id, motivo, detalhes[:80], datetime.utcnow()))
        conn.commit()
    except Exception as e:
        conn.rollback()
        return jsonify(success=False,
                       message='Erro ao registrar denúncia.'), 500
    finally:
        conn.close()

    return jsonify(success=True,
                   message='Denúncia enviada. Obrigado por ajudar a manter a comunidade segura!'), 20
# =============================================================
#  DENUNCIAR COMENTÁRIO
# =============================================================
@denuncia_bp.route('/denunciar_comentario', methods=['POST'])
def denunciar_comentario():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return jsonify(success=False, message='Você precisa estar logado para denunciar.'), 401

    if request.is_json:
        data = request.get_json(silent=True) or {}
        try:
            comentario_id = int(data.get('comentario_id')) if data.get('comentario_id') else None
            post_id = int(data.get('post_id')) if data.get('post_id') else None
        except ValueError:
            return jsonify(success=False, message='ID inválido.'), 400

        motivo = (data.get('motivo') or '').strip()
        detalhes = (data.get('detalhes') or '').strip()
    else:
        return jsonify(success=False, message='Requisição inválida.'), 400

    if not comentario_id or not motivo:
        return jsonify(success=False, message='Motivo da denúncia é obrigatório.'), 400

    conn = criar_conexao()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO denuncias (tipo, id_alvo, id_denunciante, motivo, descricao, data_denuncia)
                VALUES ('comentario', %s, %s, %s, %s, %s)
            """, (
                comentario_id,
                usuario_id,
                motivo,
                detalhes[:80],
                datetime.utcnow()
            ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[ERRO] ao denunciar: {e}")
        return jsonify(success=False, message='Erro ao registrar denúncia.'), 500
    finally:
        conn.close()

    return jsonify(success=True, message='Denúncia enviada com sucesso.'), 200
# =============================================================
#  DENUNCIAR PERFIL
# =============================================================
@denuncia_bp.route('/denunciar_usuario', methods=['POST'])
def denunciar():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return jsonify(success=False, message='Você precisa estar logado para denunciar.'), 401

    tipo = request.form.get('tipo')
    id_alvo = request.form.get('id_alvo')
    motivo = request.form.get('motivo', '').strip()
    detalhes = request.form.get('detalhes', '').strip()

    if not tipo or not id_alvo or not motivo:
        return jsonify(success=False, message='Todos os campos são obrigatórios.'), 400

    conn = criar_conexao()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO denuncias (tipo, id_alvo, id_denunciante, motivo, descricao, data_denuncia)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (tipo, id_alvo, usuario_id, motivo, detalhes[:80], datetime.utcnow()))
        conn.commit()
        return jsonify(success=True, message='Denúncia enviada com sucesso!')
    except Exception as e:
        conn.rollback()
        return jsonify(success=False, message='Erro ao registrar denúncia.'), 500
    finally:
        conn.close()
# =============================================================
#  DENUNCIAR MENSAGENS
# =============================================================
@denuncia_bp.route('/denunciar_mensagem', methods=['POST'])
def denunciar_mensagem():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return jsonify(success=False, message='Você precisa estar logado para denunciar.'), 401

    if request.is_json:
        data = request.get_json(silent=True) or {}
        try:
            mensagem_id = int(data.get('mensagem_id')) if data.get('mensagem_id') else None
        except ValueError:
            return jsonify(success=False, message='ID inválido.'), 400

        motivo = (data.get('motivo') or '').strip()
        detalhes = (data.get('detalhes') or '').strip()
    else:
        return jsonify(success=False, message='Requisição inválida.'), 400

    if not mensagem_id or not motivo:
        return jsonify(success=False, message='Motivo da denúncia é obrigatório.'), 400

    conn = criar_conexao()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO denuncias (tipo, id_alvo, id_denunciante, motivo, descricao, data_denuncia)
                VALUES ('mensagem', %s, %s, %s, %s, %s)
            """, (
                mensagem_id,
                usuario_id,
                motivo,
                detalhes[:80],  
                datetime.utcnow()
            ))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"[ERRO] ao denunciar mensagem: {e}")
        return jsonify(success=False, message='Erro ao registrar denúncia.'), 500
    finally:
        conn.close()

    return jsonify(success=True, message='Denúncia enviada com sucesso.'), 200