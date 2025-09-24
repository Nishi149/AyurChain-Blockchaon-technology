# emailer.py
import os
import smtplib
import ssl
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
FROM_NAME = os.getenv("FROM_NAME", "AyurChain")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)  # fallback to SMTP_USER

def send_email_with_attachments(subject, body, to_emails, attachments=None):
    """
    Send an email with optional file attachments.
    """
    if not isinstance(to_emails, (list, tuple)):
        to_emails = [to_emails]

    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        raise RuntimeError("⚠️ SMTP credentials are missing in .env file")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
    msg["To"] = ", ".join(to_emails)
    msg.set_content(body)

    # Attach files if provided
    if attachments:
        for path in attachments:
            try:
                with open(path, "rb") as f:
                    data = f.read()
                filename = os.path.basename(path)
                msg.add_attachment(data, maintype="application", subtype="octet-stream", filename=filename)
            except Exception as e:
                print(f"⚠️ Could not attach {path}: {e}")

    # Send email
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
            print("✅ Email sent successfully")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")
