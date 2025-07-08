from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify
from app.conexao import criar_conexao
from app.enviar_email import recuperacao_senha_user_logado
from datetime import datetime, timedelta
import random

recuperar_senha_bp = Blueprint('recuperar_senha', __name__)

@recuperar_senha_bp.route('/reenviar_codigo_para_recupar_senha_nao_logado', methods=['POST'])
def reenviar_codigo_para_recupar_senha_nao_logado():
    print("Sessão atual no reenviar_codigo:", dict(session))
    if 'recuperacao_user_id' not in session or 'recuperacao_email' not in session:
        print("Sessão expirada ou chaves não encontradas!")
        return jsonify({
            'success': False,
            'message': 'Sessão expirada, por favor refaça o passo 1',
            'redirect': url_for('.recuperar_senha_part1')
        }), 400

    usuario_id = session['recuperacao_user_id']
    email = session['recuperacao_email']

    conexao = criar_conexao()
    cursor = conexao.cursor(dictionary=True)

    try:
        # Invalida códigos antigos não utilizados
        agora = datetime.now()
        cursor.execute("""
            UPDATE recuperacao_senha 
            SET expirado_em = %s 
            WHERE user_id = %s AND utilizado_em IS NULL AND expirado_em IS NULL
        """, (agora, usuario_id))

        # Gera novo código
        codigo = str(random.randint(100000, 999999))

        cursor.execute("""
            INSERT INTO recuperacao_senha (user_id, codigo, criado_em, ip_criacao)
            VALUES (%s, %s, %s, %s)
        """, (usuario_id, codigo, agora, request.remote_addr))

        conexao.commit()

        # Envia email com o novo código
        cursor.execute("SELECT username FROM users WHERE id = %s", (usuario_id,))
        user = cursor.fetchone()
        username = user['username'] if user else 'Usuário'

        recuperacao_senha_user_logado(email, codigo, username)

        # Atualiza validade na sessão para 15 minutos a partir de agora
        session['recuperacao_validade'] = (agora + timedelta(minutes=15)).isoformat()

        return jsonify({'success': True})

    except Exception as e:
        print(f"Erro ao reenviar código: {e}")
        return jsonify({'success': False, 'message': 'Erro interno ao reenviar código'}), 500

    finally:
        cursor.close()
        conexao.close()

@recuperar_senha_bp.route('/recuperar_senha_part1', methods=['GET', 'POST'])
def recuperar_senha_part1():
    if 'usuario_id' in session:
        return redirect(url_for('inicio.inicio'))

    sucesso = False
    erro_email = False
    email = ''

    if request.method == 'POST':
        email = request.form.get('email')

        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute("SELECT id, username FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()

            if not user:
                erro_email = True
            else:
                usuario_id = user['id']
                username = user['username']
                agora = datetime.now()

                # Invalida códigos antigos
                cursor.execute("""
                    UPDATE recuperacao_senha 
                    SET expirado_em = %s 
                    WHERE user_id = %s AND utilizado_em IS NULL AND expirado_em IS NULL
                """, (agora, usuario_id))

                # Gera e envia novo código
                codigo = str(random.randint(100000, 999999))
                cursor.execute("""
                    INSERT INTO recuperacao_senha (user_id, codigo, criado_em, ip_criacao)
                    VALUES (%s, %s, %s, %s)
                """, (usuario_id, codigo, agora, request.remote_addr))
                conexao.commit()

                session['recuperacao_user_id'] = usuario_id
                session['recuperacao_email'] = email
                session['recuperacao_validade'] = (agora + timedelta(minutes=15)).isoformat()

                recuperacao_senha_user_logado(email, codigo, username)
                sucesso = True

        finally:
            cursor.close()
            conexao.close()

    return render_template('recuperar_senha_parte1.html', sucesso=sucesso, erro_email=erro_email, email=email)




@recuperar_senha_bp.route('/recuperar_senha_part2', methods=['GET', 'POST'])
def recuperar_senha_part2():
    print("Sessão em part2:", dict(session))
    if 'recuperacao_user_id' not in session:
        return redirect(url_for('.recuperar_senha_part1'))

    usuario_id = session['recuperacao_user_id']
    erro_codigo = False
    sucesso = False

    if request.method == 'POST':
        codigo = request.form.get('codigo')
        agora = datetime.now()

        conexao = criar_conexao()
        cursor = conexao.cursor(dictionary=True)
        try:
            cursor.execute("""
                SELECT id FROM recuperacao_senha 
                WHERE user_id=%s AND codigo=%s AND utilizado_em IS NULL AND expirado_em IS NULL
                AND criado_em >= %s
                ORDER BY criado_em DESC LIMIT 1
            """, (usuario_id, codigo, agora - timedelta(minutes=15)))

            row = cursor.fetchone()
            if row:
                cursor.execute("UPDATE recuperacao_senha SET utilizado_em=%s WHERE id=%s", (agora, row['id']))
                conexao.commit()
                session['codigo_validado'] = True
                sucesso = True  # <- Sucesso
            else:
                erro_codigo = True  # <- Código incorreto

        finally:
            cursor.close()
            conexao.close()

    return render_template(
        'recuperar_senha_parte2.html',
        erro_codigo=erro_codigo,
        sucesso=sucesso
    )

@recuperar_senha_bp.route('/recuperar_senha_part3', methods=['GET', 'POST'])
def recuperar_senha_part3():
    if not session.get('codigo_validado') or 'recuperacao_user_id' not in session:
        return redirect(url_for('.recuperar_senha_part1'))

    usuario_id = session['recuperacao_user_id']

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        nova = data.get('nova_senha')
        confirma = data.get('confirmar_senha')

        if not nova or not confirma:
            return jsonify({'success': False, 'error': 'Preencha os dois campos'}), 400
        if nova != confirma:
            return jsonify({'success': False, 'error': 'As senhas não coincidem'}), 400
        if len(nova) < 6:
            return jsonify({'success': False, 'error': 'Mínimo 6 caracteres'}), 400

        conexao = criar_conexao()
        cursor = conexao.cursor()
        try:
            cursor.execute("UPDATE users SET senha = %s WHERE id = %s", (nova, usuario_id))
            cursor.execute("""
                UPDATE recuperacao_senha SET expirado_em = %s
                WHERE user_id = %s AND utilizado_em IS NULL AND expirado_em IS NULL
            """, (datetime.now(), usuario_id))
            conexao.commit()

            # Após alterar a senha, cria sessão do usuário para mantê-lo logado
            session.clear()  # limpa sessão anterior
            session['usuario_id'] = usuario_id

            return jsonify({'success': True, 'message': 'Senha redefinida!', 'redirect': url_for('inicio.inicio')}), 200

        finally:
            cursor.close()
            conexao.close()

    return render_template('recuperar_senha_parte3.html')
