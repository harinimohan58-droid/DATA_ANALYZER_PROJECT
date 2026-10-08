import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path
import re
import streamlit as st


def _get_email_settings():
    """Read Brevo SMTP settings from Streamlit Secrets."""
    try:
        settings = st.secrets["email"]
        return {
            "smtp_host": str(settings["smtp_host"]),
            "smtp_port": int(settings.get("smtp_port", 587)),
            "smtp_username": str(settings["smtp_username"]),
            "smtp_password": str(settings["smtp_password"]),
            "from_email": str(settings["from_email"]),
            "from_name": str(settings.get("from_name", "Data Analyzer AI")),
        }
    except Exception as exc:
        raise RuntimeError(
            "Email configuration is missing. Add the [email] section in "
            "Streamlit Cloud → Settings → Secrets."
        ) from exc


def _valid_email(address):
    pattern = r"^[^\s@]+@[^\s@]+\.[^\s@]+$"
    return bool(re.match(pattern, address or ""))


def send_report_email(
    recipient_email: str,
    pdf_path: str,
    subject: str = "Data Analyzer AI - Business Analysis Report",
):
    """Send the generated PDF through Brevo SMTP."""
    try:
        recipient_email = (recipient_email or "").strip()

        if not recipient_email:
            return False, "Please enter a recipient email address."

        if not _valid_email(recipient_email):
            return False, "Please enter a valid recipient email address."

        pdf_file = Path(pdf_path)
        if not pdf_file.exists():
            return False, "The generated PDF report could not be found."

        if pdf_file.stat().st_size == 0:
            return False, "The generated PDF report is empty."

        settings = _get_email_settings()

        if not _valid_email(settings["from_email"]):
            return False, "The configured sender email is invalid."

        message = EmailMessage()
        message["Subject"] = subject
        message["From"] = (
            f"{settings['from_name']} <{settings['from_email']}>"
            if settings["from_name"]
            else settings["from_email"]
        )
        message["To"] = recipient_email

        message.set_content(
            "Hello,\n\n"
            "Please find attached your Data Analyzer AI business analysis report.\n\n"
            "The report was generated from the data uploaded to the Data Analyzer AI application.\n\n"
            "Regards,\n"
            "Data Analyzer AI"
        )

        with pdf_file.open("rb") as file:
            pdf_data = file.read()

        message.add_attachment(
            pdf_data,
            maintype="application",
            subtype="pdf",
            filename="automated_bi_report.pdf",
        )

        context = ssl.create_default_context()

        with smtplib.SMTP(
            settings["smtp_host"],
            settings["smtp_port"],
            timeout=30,
        ) as server:
            server.ehlo()
            server.starttls(context=context)
            server.ehlo()
            server.login(
                settings["smtp_username"],
                settings["smtp_password"],
            )
            server.send_message(message)

        return True, f"Report successfully sent to {recipient_email}."

    except smtplib.SMTPAuthenticationError:
        return (
            False,
            "Brevo SMTP authentication failed. Check the SMTP login and SMTP key in Streamlit Secrets.",
        )
    except smtplib.SMTPConnectError:
        return False, "Could not connect to the Brevo SMTP server."
    except TimeoutError:
        return False, "The email server connection timed out. Please try again."
    except smtplib.SMTPException as exc:
        return False, f"Brevo SMTP error: {exc}"
    except RuntimeError as exc:
        return False, str(exc)
    except Exception as exc:
        return False, f"Email sending failed: {exc}"
