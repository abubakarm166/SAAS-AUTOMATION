"""Send transactional emails from the API (password reset, etc.)."""
from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage

from app.config import settings

logger = logging.getLogger(__name__)


def smtp_configured() -> bool:
    return bool(settings.smtp_username and settings.smtp_password)


def send_email(*, to: str, subject: str, body: str) -> bool:
    """Send a plain-text email. Returns True on success."""
    if not smtp_configured():
        logger.warning("SMTP not configured — email to %s not sent: %s", to, subject)
        return False

    sender = settings.smtp_from or settings.smtp_username
    password = settings.smtp_password.replace(" ", "").strip()

    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(settings.smtp_host, settings.smtp_port, context=context) as smtp:
            smtp.login(settings.smtp_username.strip(), password)
            smtp.send_message(msg)
        logger.info("Email sent to %s (%s)", to, subject)
        return True
    except Exception:
        logger.exception("Failed to send email to %s", to)
        return False
