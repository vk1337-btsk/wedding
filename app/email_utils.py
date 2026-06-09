import smtplib
from email.message import EmailMessage

from .config import settings


def format_response_message(invitation: dict, response: dict) -> EmailMessage:
    body = (
        f"Гость: {invitation['guest_name']}\n"
        f"Придут: {'Да' if response['attendance'] else 'Нет'}\n"
        f"Количество гостей: {response['guest_count'] or 0}\n"
        f"Дети: {'Да' if response['children'] else 'Нет'}\n"
        f"Вегетарианское меню: {'Да' if response['vegetarian'] else 'Нет'}\n"
        f"Аллергии: {response['allergies'] or 'Нет'}\n"
        f"Телефон: {response['phone'] or '-'}\n"
        f"Telegram: {response['telegram'] or '-'}\n"
        f"Комментарий: {response['comment'] or '-'}\n"
        f"Дата ответа: {response['answered_at']}\n"
    )
    message = EmailMessage()
    message["Subject"] = f"Новый RSVP: {invitation['guest_name']}"
    message["From"] = settings.email_from
    message["To"] = settings.notify_to
    message.set_content(body)
    return message


def send_response_email(invitation: dict, response: dict) -> None:
    message = format_response_message(invitation, response)
    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
        if settings.smtp_user and settings.smtp_password:
            smtp.starttls()
            smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(message)
