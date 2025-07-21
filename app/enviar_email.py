import os
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv   

load_dotenv()  

# =============================================================
#  ENVIAR O EMAIL PARA RECUPERAR SENHA
# ============================================================= 
def recuperacao_senha_user_logado(email, codigo, username):
    
    smtp_server   = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port     = int(os.getenv("SMTP_PORT", 587))
    smtp_user     = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD", "").replace(" ", "")  

    if not all([smtp_user, smtp_password]):
        raise RuntimeError("SMTP_USER ou SMTP_PASSWORD não configurados no .env")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Código de Recuperação de Senha</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 0;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
                color: white;
                padding: 30px 20px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .content {{
                padding: 30px;
            }}
            .code-box {{
                background-color: #f8f9fa;
                border: 1px dashed #6e48aa;
                border-radius: 5px;
                padding: 15px;
                text-align: center;
                margin: 20px 0;
                font-size: 28px;
                font-weight: bold;
                color: #6e48aa;
            }}
            .footer {{
                background-color: #f1f1f1;
                padding: 15px;
                text-align: center;
                font-size: 12px;
                color: #777;
            }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 15px 0;
                font-weight: bold;
            }}
            .note {{
                font-size: 14px;
                color: #666;
                margin-top: 20px;
                line-height: 1.5;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
             <img src="https://i.imgur.com/hAFfeJH.png" alt="Logo" style="max-height: 60px; display: block; margin: 0 auto 15px;">
                <h1>Alteração de Senha</h1>
            </div>
            
            <div class="content">
                <p>Olá, {username}</p>
                <p>Recebemos uma solicitação para alterar a senha da sua conta. Utilize o código abaixo para prosseguir:</p>
                
                <div class="code-box">
                    {codigo}
                </div>
                
                <p>Este código é válido por 15 minutos. Se você não solicitou esta alteração, por favor ignore este e-mail.</p>
                
            </div>
            
            <div class="footer">
                <p>© 2025 Sirius Network Media Social. Todos os direitos reservados.</p>
                <p>Este é um e-mail automático, por favor não responda.</p>
            </div>
        </div>
    </body>
    </html>
    """
    msg = EmailMessage()
    msg['Subject'] = f'Olá {username}, seu código de alteração de senha'
    msg['From'] = smtp_user
    msg['To'] = email
    
    msg.set_content(f"""Olá {username},

    Seu código para alteração de senha é: {codigo}

    Este código é válido por 15 minutos. Se você não solicitou esta alteração, por favor ignore este e-mail.""")
    
    msg.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print(f"Código enviado para {email}")
    except Exception as e:
        print(f"Erro ao enviar email: {e}")
# =============================================================
#  ENVIAR O EMAIL PARA CONFIRMAR CONTA
# ============================================================= 
def confirmacao_conta_email(email, codigo, username):
    
    smtp_server   = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port     = int(os.getenv("SMTP_PORT", 587))
    smtp_user     = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD", "").replace(" ", "")  

    if not all([smtp_user, smtp_password]):
        raise RuntimeError("SMTP_USER ou SMTP_PASSWORD não configurados no .env")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Confirmação de Conta</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f5f5;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
                color: white;
                padding: 30px 20px;
                text-align: center;
            }}
            .code-box {{
                background-color: #f8f9fa;
                border: 1px dashed #6e48aa;
                border-radius: 5px;
                padding: 15px;
                text-align: center;
                margin: 20px 0;
                font-size: 28px;
                font-weight: bold;
                color: #6e48aa;
            }}
            .content {{
                padding: 30px;
            }}
            .footer {{
                background-color: #f1f1f1;
                padding: 15px;
                text-align: center;
                font-size: 12px;
                color: #777;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="https://i.imgur.com/hAFfeJH.png" alt="Logo" style="max-height: 60px; margin-bottom: 10px;">
                <h1>Confirmação de Conta</h1>
            </div>
            <div class="content">
                <p>Olá, {username}!</p>
                <p>Obrigado por se cadastrar. Use o código abaixo para confirmar sua conta:</p>
                <div class="code-box">{codigo}</div>
                <p>Este código é válido por 15 minutos.</p>
            </div>
            <div class="footer">
                <p>© 2025 Sirius Network Media Social. Todos os direitos reservados.</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = EmailMessage()
    msg['Subject'] = 'Confirmação de Conta - Sirius Network'
    msg['From'] = smtp_user
    msg['To'] = email

    msg.set_content(f"""Olá {username},

    Obrigado por se cadastrar na Sirius Network Media Social!

    Seu código de confirmação é: {codigo}

    Este código é válido por 15 minutos.
    """)

    msg.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print(f"E-mail de confirmação enviado para {email}")
        return True
    except Exception as e:
        print(f"Erro ao enviar e-mail: {e}")
        return False
# =============================================================
#  ENVIAR O EMAIL APOS A SUSPENSÃO
# ============================================================= 
def enviar_email_suspensao_user(email, username):
    
    smtp_server   = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port     = int(os.getenv("SMTP_PORT", 587))
    smtp_user     = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD", "").replace(" ", "")  

    if not all([smtp_user, smtp_password]):
        raise RuntimeError("SMTP_USER ou SMTP_PASSWORD não configurados no .env")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 0;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
                color: white;
                padding: 30px 20px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .content {{
                padding: 30px;
            }}
            .code-box {{
                background-color: #f8f9fa;
                border: 1px dashed #6e48aa;
                border-radius: 5px;
                padding: 15px;
                text-align: center;
                margin: 20px 0;
                font-size: 28px;
                font-weight: bold;
                color: #6e48aa;
            }}
            .footer {{
                background-color: #f1f1f1;
                padding: 15px;
                text-align: center;
                font-size: 12px;
                color: #777;
            }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 15px 0;
                font-weight: bold;
            }}
            .note {{
                font-size: 14px;
                color: #666;
                margin-top: 20px;
                line-height: 1.5;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="https://i.imgur.com/hAFfeJH.png" alt="Logo" style="max-height: 60px; display: block; margin: 0 auto 15px;">
                <h1>Conta suspensa</h1>
            </div>
            <div class="content">
                <p>Olá, <strong>{username}</strong>,</p>
                <p>Informamos que sua conta foi <strong>suspensa</strong> por violar os termos de uso da plataforma <strong>Sirius</strong>.</p>
                <p>Enquanto estiver suspenso, você não poderá acessar a rede social. Caso a suspensão tenha sido um engano, entre em contato com o suporte.</p>
            </div>
            <div class="footer">
                <p>&copy; 2025 Sirius Network Media Social. Todos os direitos reservados.</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = EmailMessage()
    msg['Subject'] = f"Conta suspensa - Sirius"
    msg['From'] = smtp_user
    msg['To'] = email

    msg.set_content(f"""Olá {username},

    Sua conta foi suspensa por violar os termos da plataforma Sirius. Entre em contato com o suporte se acredita que foi um engano.""")
    msg.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print(f"E-mail de suspensão enviado para {email}")
    except Exception as e:
        print(f"Erro ao enviar e-mail de suspensão: {e}")
# =============================================================
#  ENVIAR O EMAIL APOS A REMOÇÃO DA SUSPENSÃO
# ============================================================= 
def enviar_email_remocao_suspensao_user(email, username):
    
    smtp_server   = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port     = int(os.getenv("SMTP_PORT", 587))
    smtp_user     = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD", "").replace(" ", "")  

    if not all([smtp_user, smtp_password]):
        raise RuntimeError("SMTP_USER ou SMTP_PASSWORD não configurados no .env")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Suspensão Removida</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 0;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
                color: white;
                padding: 30px 20px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .content {{
                padding: 30px;
            }}
            .code-box {{
                background-color: #f8f9fa;
                border: 1px dashed #6e48aa;
                border-radius: 5px;
                padding: 15px;
                text-align: center;
                margin: 20px 0;
                font-size: 28px;
                font-weight: bold;
                color: #6e48aa;
            }}
            .footer {{
                background-color: #f1f1f1;
                padding: 15px;
                text-align: center;
                font-size: 12px;
                color: #777;
            }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 15px 0;
                font-weight: bold;
            }}
            .note {{
                font-size: 14px;
                color: #666;
                margin-top: 20px;
                line-height: 1.5;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="https://i.imgur.com/hAFfeJH.png" alt="Logo" style="max-height: 60px; display: block; margin: 0 auto 15px;">
                <h1>Suspensão Removida</h1>
            </div>
            <div class="content">
                <p>Olá, {username},</p>
                <p>Sua suspensão foi removida e você já pode acessar sua conta normalmente.</p>
                <p>Se você tiver qualquer dúvida ou precisar de ajuda, estamos à disposição.</p>
                <p>Bem-vindo(a) de volta!</p>
            </div>
            <div class="footer">
                <p>© 2025 Sirius Network Media Social. Todos os direitos reservados.</p>
                <p>Este é um e-mail automático, por favor não responda.</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = EmailMessage()
    msg['Subject'] = f'Suspensão removida - Seja bem-vindo(a) de volta, {username}!'
    msg['From'] = smtp_user
    msg['To'] = email
    msg.set_content(f"""Olá, {username},

Sua suspensão foi removida e você já pode acessar sua conta normalmente.

Se tiver dúvidas, estamos à disposição.

Este é um e-mail automático, por favor não responda.
""")
    msg.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print(f"E-mail de remoção de suspensão enviado para {email}")
    except Exception as e:
        print(f"Erro ao enviar email de remoção de suspensão: {e}")
# =============================================================
#  ENVIAR O EMAIL APOS A REMOÇÃO DO POST 
# ============================================================= 
def enviar_email_remocao_post(email, username):

    smtp_server   = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port     = int(os.getenv("SMTP_PORT", 587))
    smtp_user     = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD", "").replace(" ", "")  

    if not all([smtp_user, smtp_password]):
        raise RuntimeError("SMTP_USER ou SMTP_PASSWORD não configurados no .env") 

    assunto = "Post removido - Sirius Network"
    html_content = f""" <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Post Removida</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 0;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
                color: white;
                padding: 30px 20px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .content {{
                padding: 30px;
            }}
            .code-box {{
                background-color: #f8f9fa;
                border: 1px dashed #6e48aa;
                border-radius: 5px;
                padding: 15px;
                text-align: center;
                margin: 20px 0;
                font-size: 28px;
                font-weight: bold;
                color: #6e48aa;
            }}
            .footer {{
                background-color: #f1f1f1;
                padding: 15px;
                text-align: center;
                font-size: 12px;
                color: #777;
            }}
            .button {{
                display: inline-block;
                padding: 12px 24px;
                background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 15px 0;
                font-weight: bold;
            }}
            .note {{
                font-size: 14px;
                color: #666;
                margin-top: 20px;
                line-height: 1.5;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="https://i.imgur.com/hAFfeJH.png" alt="Logo" style="max-height: 60px; display: block; margin: 0 auto 15px;">
                <h1>Suspensão Removida</h1>
            </div>
            <div class="content">
                <p>Olá, {username},</p>
                <p>Informamos que um de seus posts foi <strong>removido</strong> por violar as diretrizes da comunidade da Sirius.</p>
                <p style="font-size: 12px; color: #888;">Este é um e-mail automático. Por favor, não responda.</p>
            </div>
            <div class="footer">
                <p>© 2025 Sirius Network Media Social. Todos os direitos reservados.</p>
                <p>Este é um e-mail automático, por favor não responda.</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = EmailMessage()
    msg['Subject'] = assunto
    msg['From'] = smtp_user
    msg['To'] = email
    msg.set_content(f"Olá, {username},\n\nSeu post foi removido por violar nossas diretrizes.\n\nSirius Network.")
    msg.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print(f"E-mail de remoção de post enviado para {email}")
    except Exception as e:
        print(f"Erro ao enviar email de remoção de post: {e}")
# =============================================================
#  ENVIAR O EMAIL APOS A REMOÇÃO DO COMENTARIO
# ============================================================= 
def enviar_email_remocao_comentario(email, username):
    
    smtp_server   = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port     = int(os.getenv("SMTP_PORT", 587))
    smtp_user     = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD", "").replace(" ", "")  

    if not all([smtp_user, smtp_password]):
        raise RuntimeError("SMTP_USER ou SMTP_PASSWORD não configurados no .env")

    assunto = "Comentário removido - Sirius Network"
    html_content = f"""<!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Comentário Removido</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 0;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
                color: white;
                padding: 30px 20px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .content {{
                padding: 30px;
            }}
            .footer {{
                background-color: #f1f1f1;
                padding: 15px;
                text-align: center;
                font-size: 12px;
                color: #777;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="https://i.imgur.com/hAFfeJH.png" alt="Logo" style="max-height: 60px; display: block; margin: 0 auto 15px;">
                <h1>Comentário Removido</h1>
            </div>
            <div class="content">
                <p>Olá, {username},</p>
                <p>Informamos que um de seus comentários foi <strong>removido</strong> por violar as diretrizes da comunidade da Sirius.</p>
                <p style="font-size: 12px; color: #888;">Este é um e-mail automático. Por favor, não responda.</p>
            </div>
            <div class="footer">
                <p>© 2025 Sirius Network Media Social. Todos os direitos reservados.</p>
                <p>Este é um e-mail automático, por favor não responda.</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = EmailMessage()
    msg['Subject'] = assunto
    msg['From'] = smtp_user
    msg['To'] = email
    msg.set_content(f"Olá, {username},\n\nSeu comentário foi removido por violar nossas diretrizes.\n\nSirius Network.")
    msg.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print(f"E-mail de remoção de comentário enviado para {email}")
    except Exception as e:
        print(f"Erro ao enviar email de remoção de comentário: {e}")
# =============================================================
#  ENVIAR O EMAIL PARA INFORMAR O DENUNCIAR SOBRE O STATUS DA DENUNCIA
# ============================================================= 
def enviar_email_status_denuncia(email: str,
                                 username: str,
                                 tipo: str,
                                 id_alvo: int,
                                 novo_status: str) -> None:

    smtp_server   = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port     = int(os.getenv("SMTP_PORT", 587))
    smtp_user     = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD", "").replace(" ", "")

    if not all([smtp_user, smtp_password]):
        raise RuntimeError("SMTP_USER ou SMTP_PASSWORD faltando no .env")

    status_legivel = {
        "pendente":    "Pendente",
        "em_analise":  "Em análise",
        "resolvido":   "Resolvido",
        "ignorado":    "Ignorado",
    }.get(novo_status, novo_status)

    assunto = "Atualização de denúncia – Sirius Network"

    html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Status da Denúncia</title>
  <style>
      body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background:#f5f5f5; margin:0; }}
      .container {{ max-width:600px; margin:20px auto; background:#fff; border-radius:10px; box-shadow:0 0 20px rgba(0,0,0,.1); overflow:hidden; }}
      .header {{ background:linear-gradient(135deg,#6e48aa 0%,#9d50bb 100%); color:#fff; text-align:center; padding:30px 20px; }}
      .header h1 {{ margin:0; font-size:24px; }}
      .content {{ padding:30px; color:#333; }}
      .footer {{ background:#f1f1f1; text-align:center; padding:15px; font-size:12px; color:#777; }}
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <img src="https://i.imgur.com/hAFfeJH.png" alt="Logo" style="max-height:60px; display:block; margin:0 auto 15px;">
      <h1>Status da sua denúncia</h1>
    </div>
    <div class="content">
      <p>Olá, {username},</p>
      <p>A denúncia que você registrou (<strong>tipo:</strong> {tipo}{id_alvo})
         teve seu status atualizado para <strong>{status_legivel}</strong>.</p>
      <p>Obrigado por ajudar a manter a Sirius uma comunidade segura e acolhedora para todos!</p>
      <p style="font-size:12px; color:#888;">Este é um e‑mail automático. Por favor, não responda diretamente.</p>
    </div>
    <div class="footer">
      <p>© 2025 Sirius Network. Todos os direitos reservados.</p>
    </div>
  </div>
</body>
</html>"""

    texto = (f"Olá, {username},\n\n"
             f"Sua denúncia (tipo: {tipo}, ID alvo: {id_alvo}) "
             f"agora está com status: {status_legivel}.\n\n"
             "Sirius Network.")

    msg = EmailMessage()
    msg["Subject"] = assunto
    msg["From"]    = smtp_user
    msg["To"]      = email
    msg.set_content(texto)
    msg.add_alternative(html_content, subtype="html")

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print(f"E‑mail de atualização de denúncia enviado para {email}")
    except Exception as e:
        print(f"Erro ao enviar e‑mail de status de denúncia: {e}")
# =============================================================
#  ENVIAR O EMAIL AO ADM REMOVER A MSG
# ============================================================= 
def enviar_email_remocao_mensagem(email, username):
    smtp_server   = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port     = int(os.getenv("SMTP_PORT", 587))
    smtp_user     = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD", "").replace(" ", "")

    if not all([smtp_user, smtp_password]):
        raise RuntimeError("SMTP_USER ou SMTP_PASSWORD não configurados no .env")

    assunto = "Mensagem removida - Sirius Network"
    html_content = f"""<!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <title>Mensagem Removida</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f5f5;
                margin: 0;
                padding: 0;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #ffffff;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 0 20px rgba(0, 0, 0, 0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
                color: white;
                padding: 30px 20px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 24px;
            }}
            .content {{
                padding: 30px;
            }}
            .footer {{
                background-color: #f1f1f1;
                padding: 15px;
                text-align: center;
                font-size: 12px;
                color: #777;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="https://i.imgur.com/hAFfeJH.png" alt="Logo" style="max-height: 60px; display: block; margin: 0 auto 15px;">
                <h1>Mensagem Removida</h1>
            </div>
            <div class="content">
                <p>Olá, {username},</p>
                <p>Informamos que uma de suas mensagens foi <strong>removida</strong> por violar as diretrizes da comunidade da Sirius.</p>
                <p style="font-size: 12px; color: #888;">Este é um e-mail automático. Por favor, não responda.</p>
            </div>
            <div class="footer">
                <p>© 2025 Sirius Network Media Social. Todos os direitos reservados.</p>
                <p>Este é um e-mail automático, por favor não responda.</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = EmailMessage()
    msg['Subject'] = assunto
    msg['From'] = smtp_user
    msg['To'] = email
    msg.set_content(f"Olá, {username},\n\nSua mensagem foi removida por violar nossas diretrizes.\n\nSirius Network.")
    msg.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print(f"E-mail de remoção de mensagem enviado para {email}")
    except Exception as e:
        print(f"Erro ao enviar email de remoção de mensagem: {e}")
# =============================================================
#  ENVIAR O EMAIL DE LOGIN
# =============================================================
def enviar_email_login(email, username, regiao, data_hora, dispositivo):
    smtp_server   = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port     = int(os.getenv("SMTP_PORT", 587))
    smtp_user     = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD", "").replace(" ", "")  

    if not all([smtp_user, smtp_password]):
        raise RuntimeError("SMTP_USER ou SMTP_PASSWORD não configurados no .env")

    html_content = f"""
    <!DOCTYPE html>
    <html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>Notificação de Login</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background-color: #f5f5f5;
                margin: 0; padding: 0; color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 20px auto;
                background-color: #fff;
                border-radius: 10px;
                box-shadow: 0 0 20px rgba(0,0,0,0.1);
                overflow: hidden;
            }}
            .header {{
                background: linear-gradient(135deg, #6e48aa 0%, #9d50bb 100%);
                color: white;
                padding: 30px 20px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0; font-size: 24px;
            }}
            .content {{
                padding: 30px;
            }}
            .info {{
                background-color: #f8f9fa;
                border-radius: 5px;
                padding: 15px;
                margin: 20px 0;
                font-size: 16px;
                line-height: 1.5;
                color: #6e48aa;
                font-weight: 600;
            }}
            .footer {{
                background-color: #f1f1f1;
                padding: 15px;
                text-align: center;
                font-size: 12px;
                color: #777;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <img src="https://i.imgur.com/hAFfeJH.png" alt="Logo" style="max-height: 60px; margin: 0 auto 15px; display: block;">
                <h1>Notificação de Login</h1>
            </div>
            <div class="content">
                <p>Olá, {username}</p>
                <p>Detectamos um novo login na sua conta com as seguintes informações:</p>
                <div class="info">
                    <p><strong>Região:</strong> {regiao}</p>
                    <p><strong>Data e Hora:</strong> {data_hora}</p>
                    <p><strong>Dispositivo:</strong> {dispositivo}</p>
                </div>
                <p>Se foi você, pode ignorar este e-mail. Se não reconhece esta atividade, por favor altere sua senha imediatamente.</p>
            </div>
            <div class="footer">
                <p>© 2025 Sirius Network Media Social. Todos os direitos reservados.</p>
                <p>Este é um e-mail automático, por favor não responda.</p>
            </div>
        </div>
    </body>
    </html>
    """

    msg = EmailMessage()
    msg['Subject'] = f'Olá {username}, novo login detectado na sua conta'
    msg['From'] = smtp_user
    msg['To'] = email

    msg.set_content(f"""Olá {username},

Detectamos um novo login na sua conta.

Região: {regiao}
Data e Hora: {data_hora}
Dispositivo: {dispositivo}

Se foi você, pode ignorar este e-mail. Se não reconhece esta atividade, por favor altere sua senha imediatamente.
""")

    msg.add_alternative(html_content, subtype='html')

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print(f"Email de login enviado para {email}")
    except Exception as e:
        print(f"Erro ao enviar email: {e}")