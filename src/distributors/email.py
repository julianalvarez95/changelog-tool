"""
Send changelog via SMTP (G Suite / Gmail App Password).
"""
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional


SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587


def send(
    gmail_address: str,
    app_password: str,
    recipients: list[str],
    subject: str,
    html_body: str,
    from_name: Optional[str] = "Changelog Bot",
) -> bool:
    """
    Send an HTML email via Gmail SMTP.
    Returns True on success, False on failure.
    """
    if not gmail_address or not app_password:
        print("[ERROR] GMAIL_ADDRESS and GMAIL_APP_PASSWORD are required to send emails.", file=sys.stderr)
        return False
    if not recipients:
        print("[WARN] No email recipients configured. Skipping email send.", file=sys.stderr)
        return False

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{from_name} <{gmail_address}>"
    msg["To"] = ", ".join(recipients)
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(gmail_address, app_password)
            server.sendmail(gmail_address, recipients, msg.as_string())
        print(f"[email] Sent to {len(recipients)} recipient(s): {', '.join(recipients)}")
        return True
    except smtplib.SMTPAuthenticationError:
        print(
            "[ERROR] SMTP authentication failed. Verify GMAIL_ADDRESS and GMAIL_APP_PASSWORD.",
            file=sys.stderr,
        )
        return False
    except smtplib.SMTPException as e:
        print(f"[ERROR] SMTP error: {e}", file=sys.stderr)
        return False
