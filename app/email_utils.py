# app\email_utils.py
import smtplib
import ssl
from email.message import EmailMessage

from .config import settings


def format_response_message(invitation: dict, response: dict) -> EmailMessage:
    will_come = response.get("will_come") == "yes"
    allergies = response.get("allergies")
    alcohol = response.get("alcohol")
    body = (
        f"Гость: {invitation['guest_name']}\n"
        f"Придёт: {'Да, конечно' if will_come else 'Нет, к сожалению'}\n"
        f"Пояснение: {response.get('comment_will_come') or '-'}\n"
        f"Аллергии: {'Да' if allergies else 'Нет'}\n"
        f"Описание аллергий: {response.get('allergies_details') or '-'}\n"
        f"Алкоголь: {'Да' if alcohol else 'Нет'}\n"
        f"Дополнительная информация: {response.get('additional_info') or '-'}\n"
        f"Дата ответа: {response['answered_at']}\n"
    )
    message = EmailMessage()
    message["Subject"] = f"Новый RSVP: {invitation['guest_name']}"
    message["From"] = settings.email
    message["To"] = settings.email
    message.set_content(body)
    return message


def send_response_email(invitation: dict, response: dict) -> None:
    import logging

    logging.info(f"SMTP_HOST={settings.smtp_host}, SMTP_PORT={settings.smtp_port}")

    message = format_response_message(invitation, response)
    try:
        if settings.smtp_port == 465:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                settings.smtp_host, 465, timeout=10, context=context
            ) as smtp:
                if settings.email and settings.smtp_password:
                    smtp.login(settings.email, settings.smtp_password)
                smtp.send_message(message)
        else:
            with smtplib.SMTP(
                settings.smtp_host, settings.smtp_port, timeout=10
            ) as smtp:
                if settings.email and settings.smtp_password:
                    smtp.starttls()
                    smtp.login(settings.email, settings.smtp_password)
                smtp.send_message(message)
    except Exception as e:
        # логируем с подробностями
        import logging

        logging.error(f"SMTP error: {e}")
        raise
