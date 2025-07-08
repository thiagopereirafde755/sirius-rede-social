import smtplib  # ou use seu método de envio de email preferido
from app.conexao import criar_conexao
import smtplib
from email.message import EmailMessage

def recuperacao_senha_user_logado(email, codigo, username):
    # Configurações do seu servidor SMTP
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "siriusnetworkmedia@gmail.com"
    smtp_password = "jgtq pgpz grwx aogg"  # Não use sua senha normal, use senha de app se for Gmail

    # HTML template bonito para o email
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
                
                <p class="note">Acesse este link para continuar:<br>
                <small>http://127.0.0.1:5000/recuperar_senha_logado_part2</small></p>
            </div>
            
            <div class="footer">
                <p>© 2025 Sirius Network Media Social. Todos os direitos reservados.</p>
                <p>Este é um e-mail automático, por favor não responda.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Montando o email
    msg = EmailMessage()
    msg['Subject'] = f'Olá {username}, seu código de alteração de senha'
    msg['From'] = smtp_user
    msg['To'] = email
    
    # Adicionando versão em texto simples e HTML
    msg.set_content(f"""Olá {username},

Seu código para alteração de senha é: {codigo}

Acesse este link para continuar: http://127.0.0.1:5000/recuperar_senha_logado_part2

Este código é válido por 15 minutos. Se você não solicitou esta alteração, por favor ignore este e-mail.""")
    
    msg.add_alternative(html_content, subtype='html')

    # Enviando
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print(f"Código enviado para {email}")
    except Exception as e:
        print(f"Erro ao enviar email: {e}")

def confirmacao_conta_email(email, codigo, username):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "siriusnetworkmedia@gmail.com"
    smtp_password = "jgtq pgpz grwx aogg"  # use uma senha de app, nunca a senha da conta

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
                <p class="note">Acesse este link para continuar:<br><small>http://127.0.0.1:5000/confirmar_conta/part2</small></p>
            </div>
            <div class="footer">
                <p>© 2025 Sirius Network Media Social. Todos os direitos reservados.</p>
            </div>
        </div>
    </body>
    </html>
    """

    # Monta o e-mail
    msg = EmailMessage()
    msg['Subject'] = 'Confirmação de Conta - Sirius Network'
    msg['From'] = smtp_user
    msg['To'] = email

    msg.set_content(f"""Olá {username},

Obrigado por se cadastrar na Sirius Network Media Social!

Seu código de confirmação é: {codigo}

Acesse este link para continuar: http://127.0.0.1:5000/confirmar_conta/part2

Este código é válido por 15 minutos.
""")

    msg.add_alternative(html_content, subtype='html')

    # Envia
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