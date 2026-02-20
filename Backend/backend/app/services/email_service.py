"""
Service d'envoi d'emails via SMTP (Gmail).

Fonctionnalites :
- Envoi d'email generique
- Envoi de code OTP pour validation d'inscription
- Notification de paiement recu/echoue
- Renvoi de code de verification
"""

import smtplib
import logging
from email.message import EmailMessage
from typing import Optional

from app.config import settings

logger = logging.getLogger(__name__)


# ── Envoi d'email generique ─────────────────────────────

def send_email(
    to_email: str,
    subject: str,
    body: str,
    html_body: Optional[str] = None,
) -> dict:
    """
    Envoyer un email via SMTP Gmail.

    Args:
        to_email: Adresse email du destinataire
        subject: Sujet de l'email
        body: Contenu texte brut de l'email
        html_body: Contenu HTML optionnel

    Returns:
        dict avec success et error
    """
    if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
        logger.warning("Email : identifiants SMTP non configures, envoi ignore")
        return {"success": False, "error": "Identifiants SMTP non configures"}

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_HOST_USER}>"
    msg["To"] = to_email
    msg.set_content(body)

    if html_body:
        msg.add_alternative(html_body, subtype="html")

    try:
        with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT) as smtp:
            smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            smtp.send_message(msg)

        logger.info("Email : envoye avec succes a %s (sujet: %s)", to_email, subject)
        return {"success": True, "error": None}

    except smtplib.SMTPAuthenticationError:
        logger.error("Email : echec authentification SMTP pour %s", settings.EMAIL_HOST_USER)
        return {"success": False, "error": "Echec authentification SMTP. Verifiez les identifiants."}
    except smtplib.SMTPException as e:
        logger.error("Email : erreur SMTP - %s", str(e))
        return {"success": False, "error": f"Erreur SMTP: {str(e)}"}
    except Exception as e:
        logger.error("Email : erreur inattendue - %s", str(e))
        return {"success": False, "error": f"Erreur inattendue: {str(e)}"}


# ── Emails pre-formates ───────────────────────────────────

def send_verification_email(to_email: str, code: str, full_name: str) -> dict:
    """
    Envoyer un email de verification d'inscription avec code OTP.
    """
    subject = f"EcoLearn AI - Code de confirmation"

    body = (
        f"Bonjour {full_name} !\n\n"
        f"Voici votre code de confirmation : {code}\n\n"
        f"Ce code est valable pendant {settings.OTP_EXPIRY_MINUTES} minutes.\n\n"
        f"Si vous n'etes pas a l'origine de cette demande, ignorez ce message.\n\n"
        f"Bien a vous,\n"
        f"L'equipe EcoLearn AI"
    )

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; padding: 20px; background-color: #10B981; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">EcoLearn AI</h1>
            <p style="color: #D1FAE5; margin: 5px 0 0 0;">Plateforme d'apprentissage ecologique</p>
        </div>
        <div style="padding: 30px; background-color: #F9FAFB; border: 1px solid #E5E7EB; border-top: none; border-radius: 0 0 10px 10px;">
            <h2 style="color: #1F2937;">Bonjour {full_name} !</h2>
            <p style="color: #4B5563; font-size: 16px;">Voici votre code de confirmation :</p>
            <div style="text-align: center; margin: 30px 0;">
                <span style="display: inline-block; font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #10B981; background-color: #ECFDF5; padding: 15px 30px; border-radius: 10px; border: 2px dashed #10B981;">
                    {code}
                </span>
            </div>
            <p style="color: #6B7280; font-size: 14px;">
                Ce code est valable pendant <strong>{settings.OTP_EXPIRY_MINUTES} minutes</strong>.
            </p>
            <p style="color: #6B7280; font-size: 14px;">
                Si vous n'etes pas a l'origine de cette demande, ignorez ce message.
            </p>
            <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 20px 0;">
            <p style="color: #9CA3AF; font-size: 12px; text-align: center;">
                EcoLearn AI - Apprenez intelligemment, agissez ecologiquement.
            </p>
        </div>
    </body>
    </html>
    """

    return send_email(to_email, subject, body, html_body)


def send_resend_otp_email(to_email: str, code: str) -> dict:
    """
    Renvoyer un code OTP de verification par email.
    """
    subject = "EcoLearn AI - Nouveau code de verification"

    body = (
        f"EcoLearn AI - Nouveau code de verification\n\n"
        f"Votre nouveau code est : {code}\n\n"
        f"Ce code est valable pendant {settings.OTP_EXPIRY_MINUTES} minutes.\n\n"
        f"Bien a vous,\n"
        f"L'equipe EcoLearn AI"
    )

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; padding: 20px; background-color: #10B981; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">EcoLearn AI</h1>
        </div>
        <div style="padding: 30px; background-color: #F9FAFB; border: 1px solid #E5E7EB; border-top: none; border-radius: 0 0 10px 10px;">
            <h2 style="color: #1F2937;">Nouveau code de verification</h2>
            <p style="color: #4B5563;">Vous avez demande un nouveau code. Le voici :</p>
            <div style="text-align: center; margin: 30px 0;">
                <span style="display: inline-block; font-size: 36px; font-weight: bold; letter-spacing: 8px; color: #10B981; background-color: #ECFDF5; padding: 15px 30px; border-radius: 10px; border: 2px dashed #10B981;">
                    {code}
                </span>
            </div>
            <p style="color: #6B7280; font-size: 14px;">
                Ce code expire dans <strong>{settings.OTP_EXPIRY_MINUTES} minutes</strong>.
            </p>
            <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 20px 0;">
            <p style="color: #9CA3AF; font-size: 12px; text-align: center;">
                EcoLearn AI - Apprenez intelligemment, agissez ecologiquement.
            </p>
        </div>
    </body>
    </html>
    """

    return send_email(to_email, subject, body, html_body)


def send_payment_confirmation_email(
    to_email: str,
    full_name: str,
    amount: float,
    currency: str,
    plan: str,
    transaction_ref: str,
) -> dict:
    """
    Envoyer une notification email de confirmation de paiement.
    """
    subject = "EcoLearn AI - Paiement confirme"

    body = (
        f"Bonjour {full_name},\n\n"
        f"Votre paiement de {amount:.2f} {currency} "
        f"pour l'abonnement {plan.capitalize()} a ete recu avec succes.\n\n"
        f"Reference : {transaction_ref}\n\n"
        f"Votre abonnement est maintenant actif. Bon apprentissage !\n\n"
        f"Bien a vous,\n"
        f"L'equipe EcoLearn AI"
    )

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; padding: 20px; background-color: #10B981; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">EcoLearn AI</h1>
        </div>
        <div style="padding: 30px; background-color: #F9FAFB; border: 1px solid #E5E7EB; border-top: none; border-radius: 0 0 10px 10px;">
            <h2 style="color: #1F2937;">Paiement confirme !</h2>
            <p style="color: #4B5563;">Bonjour {full_name},</p>
            <div style="background-color: #ECFDF5; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <table style="width: 100%; color: #374151;">
                    <tr><td style="padding: 5px 0; font-weight: bold;">Montant :</td><td style="text-align: right;">{amount:.2f} {currency}</td></tr>
                    <tr><td style="padding: 5px 0; font-weight: bold;">Plan :</td><td style="text-align: right;">{plan.capitalize()}</td></tr>
                    <tr><td style="padding: 5px 0; font-weight: bold;">Reference :</td><td style="text-align: right; font-family: monospace;">{transaction_ref}</td></tr>
                </table>
            </div>
            <p style="color: #10B981; font-weight: bold;">Votre abonnement est maintenant actif. Bon apprentissage !</p>
            <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 20px 0;">
            <p style="color: #9CA3AF; font-size: 12px; text-align: center;">
                EcoLearn AI - Apprenez intelligemment, agissez ecologiquement.
            </p>
        </div>
    </body>
    </html>
    """

    return send_email(to_email, subject, body, html_body)


def send_payment_failed_email(
    to_email: str,
    full_name: str,
    amount: float,
    currency: str,
) -> dict:
    """
    Envoyer une notification email d'echec de paiement.
    """
    subject = "EcoLearn AI - Echec de paiement"

    body = (
        f"Bonjour {full_name},\n\n"
        f"Votre paiement de {amount:.2f} {currency} n'a pas abouti.\n\n"
        f"Veuillez reessayer ou contacter le support.\n\n"
        f"Bien a vous,\n"
        f"L'equipe EcoLearn AI"
    )

    html_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
        <div style="text-align: center; padding: 20px; background-color: #EF4444; border-radius: 10px 10px 0 0;">
            <h1 style="color: white; margin: 0;">EcoLearn AI</h1>
        </div>
        <div style="padding: 30px; background-color: #F9FAFB; border: 1px solid #E5E7EB; border-top: none; border-radius: 0 0 10px 10px;">
            <h2 style="color: #1F2937;">Echec de paiement</h2>
            <p style="color: #4B5563;">Bonjour {full_name},</p>
            <p style="color: #4B5563;">Votre paiement de <strong>{amount:.2f} {currency}</strong> n'a pas abouti.</p>
            <p style="color: #4B5563;">Veuillez reessayer ou contacter notre equipe de support.</p>
            <hr style="border: none; border-top: 1px solid #E5E7EB; margin: 20px 0;">
            <p style="color: #9CA3AF; font-size: 12px; text-align: center;">
                EcoLearn AI - Apprenez intelligemment, agissez ecologiquement.
            </p>
        </div>
    </body>
    </html>
    """

    return send_email(to_email, subject, body, html_body)
