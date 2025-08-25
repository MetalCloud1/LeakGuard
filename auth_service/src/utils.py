# -----------------------------------------------------------------------------
# Template created by Gilbert Ramirez GitHub: https://github.com/MetalCloud1
# Licensed under CC BY-NC-ND (custom) – see LICENSE.md for details
# You may view, study, and modify this template.
# Substantial modifications that add new functionality or transform the project
# may be used as your own work, as long as the original template is properly
# acknowledged.
# -----------------------------------------------------------------------------
import os
from passlib.context import CryptContext
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

ENV = os.getenv("ENVIRONMENT", "development")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def send_email(to_email: str, subject: str, body: str):
    """
    Env-safe email sender:
    - In development, prints the email to console
    - In production, sends real email using SMTP
    """
    if ENV != "production":
        print(f"[DEV EMAIL] To: {to_email}\nSubject: {subject}\n\n{body}\n")
        return

    if not SENDER_EMAIL or not SENDER_PASSWORD:
        raise RuntimeError(
            "SENDER_EMAIL and SENDER_PASSWORD must be set in production"
        )

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.send_message(msg)
    server.quit()