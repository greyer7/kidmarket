import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.core.config import settings

logger = logging.getLogger(__name__)


def send_email(to_email: str, subject: str, html_body: str) -> None:
    
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

def send_verification_email(to_email: str, full_name: str, verify_link: str) -> None:
    
    subject = "Підтвердіть свій email - KidMarket"
    html_body = f"""
    <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <h2>Привіт, {full_name}!</h2>
            <p>Дякуємо за реєстрацію в KidMarket. Щоб підтвердити свій email
               і активувати всі можливості акаунту, натисніть кнопку нижче.</p>
            <p>
                <a href="{verify_link}"
                   style="display: inline-block; padding: 12px 24px; background-color: #16A34A;
                          color: #ffffff; text-decoration: none; border-radius: 6px;">
                    Підтвердити email
                </a>
            </p>
            <p>Посилання дійсне протягом 24 годин.</p>
            <p>Якщо ви не реєструвались у KidMarket - просто проігноруйте цей лист.</p>
            <hr>
            <p style="color: #888; font-size: 12px;">
                Це автоматичний лист, будь ласка, не відповідайте на нього.
            </p>
        </body>
    </html>
    """
    send_email(to_email, subject, html_body)