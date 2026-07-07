"""
Відправка email-нотифікацій через Gmail SMTP.

Використовує ТІЛЬКИ вбудовані модулі Python (smtplib, email) -
жодних додаткових pip-залежностей не потрібно.

ВАЖЛИВО: функції тут - ЗВИЧАЙНІ (не async), навмисно. FastAPI BackgroundTasks
виконує звичайні (sync) функції в окремому потоці (threadpool), тому виклик
smtplib (який сам по собі блокуючий, не async) НЕ заблокує основний
event loop застосунку, поки лист відправляється.
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, html_body: str) -> None:
    """
    Базова функція відправки одного email-листа.

    Навмисно "проковтує" (логує, але не піднімає далі) будь-які помилки -
    якщо лист не надіслався (наприклад, Gmail тимчасово недоступний),
    це НЕ повинно ламати роботу застосунку. Користувач уже отримав
    свою відповідь (JWT-токен) до того, як ця функція взагалі почала
    виконуватись - лист це лише додатковий бонус, не критична частина логіки.
    """
    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
    message["To"] = to_email
    message.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()  # вмикаємо шифроване з'єднання
            server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(
                settings.SMTP_FROM_EMAIL,
                to_email,
                message.as_string(),
            )
        logger.info(f"Email успішно надіслано на {to_email}")
    except Exception as e:
        logger.error(f"Не вдалося надіслати email на {to_email}: {e}")


def send_google_login_notification(to_email: str, full_name: str) -> None:
    """
    Лист-нотифікація: "Ви щойно увійшли через Google".
    Викликається як фонова задача (BackgroundTasks) з google_oauth.py.
    """
    subject = "Вхід через Google - KidMarket"
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2>Привіт, {full_name}!</h2>
            <p>Ви щойно увійшли в KidMarket за допомогою вашого облікового запису Google.</p>
            <p>Якщо це були не ви - будь ласка, перевірте безпеку свого Google-акаунту.</p>
            <hr>
            <p style="color: #888; font-size: 12px;">
                Це автоматичний лист, будь ласка, не відповідайте на нього.
            </p>
        </body>
    </html>
    """
    send_email(to_email, subject, html_body)