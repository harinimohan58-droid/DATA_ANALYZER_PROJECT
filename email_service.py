import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path

import streamlit as st


def send_report_email(
    recipient_email: str,
    pdf_path: str,
    subject: str = "Data Analyzer AI - Business Analysis Report",
):
    """
    Send the generated PDF report through Gmail SMTP.

    Returns:
        (True, success_message)
        or
        (False, error_message)
    """

    try:
        recipient_email = recipient_email.strip()

        if not recipient_email:
            return False, "Please enter a recipient email address."

        if "@" not in recipient_email or "." not in recipient_email:
            return False, "Please enter a valid email address."

        pdf_file = Path(pdf_path)

        if not pdf_file.exists():
            return False, "The PDF report file could not be found."

        # ---------------------------------------------------------
        # Read Streamlit secrets
        # ---------------------------------------------------------
        try:
            smtp_host = st.secrets["email"]["smtp_host"]
            smtp_port = int(st.secrets["email"]["smtp_port"])
            smtp_username = st.secrets["email"]["smtp_username"]
            smtp_password = st.secrets["email"]["smtp_password"]
            from_email = st.secrets["email"]["from_email"]
        except Exception:
            return (
                False,
                "Email configuration is missing. "
                "Please configure the [email] section in Streamlit Secrets."
            )

        # ---------------------------------------------------------
        # Create email
        # ---------------------------------------------------------
        message = EmailMessage()

        message["Subject"] = subject
        message["From"] = from_email
        message["To"] = recipient_email

        message.set_content(
            """
Hello,

Please find attached your Data Analyzer AI business analysis report.

This report was generated from the data uploaded to the Data Analyzer AI application.

Regards,
Data Analyzer AI
"""
        )

        # ---------------------------------------------------------
        # Attach PDF
        # ---------------------------------------------------------
        with open(pdf_file, "rb") as file:
            pdf_data = file.read()

        message.add_attachment(
            pdf_data,
            maintype="application",
            subtype="pdf",
            filename=pdf_file.name,
        )

        # ---------------------------------------------------------
        # Gmail SMTP connection
        # ---------------------------------------------------------
        context = ssl.create_default_context()

        with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:

            server.ehlo()

            server.starttls(context=context)

            server.ehlo()

            server.login(
                smtp_username,
                smtp_password,
            )

            server.send_message(message)

        return (
            True,
            f"Report successfully sent to {recipient_email}."
        )

    except smtplib.SMTPAuthenticationError:
        return (
            False,
            "Gmail authentication failed. "
            "Check your Gmail address and App Password."
        )

    except smtplib.SMTPConnectError:
        return (
            False,
            "Could not connect to the Gmail SMTP server."
        )

    except smtplib.SMTPException as exc:
        return (
            False,
            f"Email server error: {exc}"
        )

    except Exception as exc:
        return (
            False,
            f"Email sending failed: {exc}"
        )
