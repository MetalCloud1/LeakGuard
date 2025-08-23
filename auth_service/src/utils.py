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


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def send_email(to_email: str, subject: str, body: str):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    sender_email = os.getenv("SENDER_EMAIL")
    sender_password = os.getenv("SENDER_PASSWORD")

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(sender_email, sender_password)
    server.send_message(msg)
    server.quit()
