"""
Utilidad de envío de emails transaccionales via SMTP Gmail.
Requiere GMAIL_USER y GMAIL_APP_PASSWORD en el entorno.
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from src.config import config


def send_verification_email(to_email: str, token: str) -> bool:
    """
    Envía un email de verificación con un botón que redirige al frontend.
    Retorna True si el envío fue exitoso, False en caso contrario.
    """
    if not config.GMAIL_USER or not config.GMAIL_APP_PASSWORD:
        print("[Email] GMAIL_USER o GMAIL_APP_PASSWORD no configurados.")
        return False

    verify_url = f"{config.FRONTEND_URL}/verify?token={token}"

    html = f"""
    <!DOCTYPE html>
    <html lang="es">
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 40px;">
      <div style="max-width: 480px; margin: 0 auto; background: #fff; border-radius: 8px; padding: 32px;">
        <h2 style="color: #1a1a1a;">Verificá tu email</h2>
        <p style="color: #444;">Gracias por comunicarte con nosotros. Hacé click en el botón para confirmar tu dirección de email y continuar la conversación.</p>
        <a href="{verify_url}"
           style="display: inline-block; margin-top: 16px; padding: 12px 24px;
                  background-color: #25D366; color: #fff; text-decoration: none;
                  border-radius: 6px; font-weight: bold;">
          Verificar email
        </a>
        <p style="color: #999; margin-top: 24px; font-size: 12px;">
          Este link es válido por 3 minutos. Si no solicitaste esto, ignorá este mensaje.
        </p>
      </div>
    </body>
    </html>
    """

    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Verificá tu email para continuar"
    msg["From"] = config.GMAIL_USER
    msg["To"] = to_email
    msg.attach(MIMEText(html, "html"))

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(config.GMAIL_USER, config.GMAIL_APP_PASSWORD)
            server.sendmail(config.GMAIL_USER, to_email, msg.as_string())
        print(f"[Email] Verificación enviada a {to_email}")
        return True
    except Exception as e:
        print(f"[Email] Error enviando a {to_email}: {e}")
        return False
