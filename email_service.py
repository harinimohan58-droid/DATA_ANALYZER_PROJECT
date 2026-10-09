import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path
import re

import streamlit as st


# ==========================================================
# EMAIL CONFIGURATION
# ==========================================================

def _get_email_settings():
    """
    Read Brevo SMTP settings from Streamlit Secrets.
    """

    try:

        settings = st.secrets["email"]

        smtp_host = str(
            settings.get(
                "smtp_host",
                "smtp-relay.brevo.com"
            )
        ).strip()

        smtp_port = int(
            settings.get(
                "smtp_port",
                587
            )
        )

        smtp_username = str(
            settings["smtp_username"]
        ).strip()

        smtp_password = str(
            settings["smtp_password"]
        ).strip()

        from_email = str(
            settings["from_email"]
        ).strip()

        from_name = str(
            settings.get(
                "from_name",
                "Data Analyzer AI"
            )
        ).strip()

        if not smtp_username:
            raise RuntimeError(
                "Brevo SMTP username is empty."
            )

        if not smtp_password:
            raise RuntimeError(
                "Brevo SMTP key is empty."
            )

        if not from_email:
            raise RuntimeError(
                "Brevo sender email is empty."
            )

        return {
            "smtp_host": smtp_host,
            "smtp_port": smtp_port,
            "smtp_username": smtp_username,
            "smtp_password": smtp_password,
            "from_email": from_email,
            "from_name": from_name,
        }

    except KeyError as exc:

        raise RuntimeError(
            "The [email] section is missing or incomplete "
            "in Streamlit Secrets."
        ) from exc

    except Exception as exc:

        raise RuntimeError(
            f"Unable to read email configuration: {exc}"
        ) from exc


# ==========================================================
# EMAIL VALIDATION
# ==========================================================

def _valid_email(address):

    pattern = (
        r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+"
        r"@[A-Za-z0-9-]+"
        r"(?:\.[A-Za-z0-9-]+)+$"
    )

    return bool(
        re.match(
            pattern,
            address or ""
        )
    )


# ==========================================================
# SEND REPORT EMAIL
# ==========================================================

def send_report_email(
    recipient_email: str,
    pdf_path: str,
    subject: str = (
        "Data Analyzer AI - Business Analysis Report"
    ),
):

    try:

        # --------------------------------------------------
        # RECIPIENT
        # --------------------------------------------------

        recipient_email = (
            recipient_email or ""
        ).strip()

        if not recipient_email:

            return (
                False,
                "Please enter a recipient email address."
            )

        if not _valid_email(recipient_email):

            return (
                False,
                "Please enter a valid recipient email address."
            )


        # --------------------------------------------------
        # PDF FILE
        # --------------------------------------------------

        pdf_file = Path(pdf_path)

        if not pdf_file.exists():

            return (
                False,
                f"PDF file was not found: {pdf_file}"
            )

        pdf_size = pdf_file.stat().st_size

        if pdf_size <= 0:

            return (
                False,
                "The generated PDF file is empty."
            )


        # --------------------------------------------------
        # SETTINGS
        # --------------------------------------------------

        settings = _get_email_settings()


        # --------------------------------------------------
        # VALIDATE SENDER
        # --------------------------------------------------

        if not _valid_email(
            settings["from_email"]
        ):

            return (
                False,
                "The configured Brevo sender email "
                "is invalid."
            )


        # --------------------------------------------------
        # CREATE EMAIL
        # --------------------------------------------------

        message = EmailMessage()

        message["Subject"] = subject

        if settings["from_name"]:

            message["From"] = (
                f"{settings['from_name']} "
                f"<{settings['from_email']}>"
            )

        else:

            message["From"] = settings["from_email"]

        message["To"] = recipient_email


        # --------------------------------------------------
        # EMAIL BODY
        # --------------------------------------------------

        message.set_content(
            "Hello,\n\n"
            "Please find attached your "
            "Data Analyzer AI business analysis report.\n\n"
            "The report was generated from the "
            "Data Analyzer AI application.\n\n"
            "Regards,\n"
            "Data Analyzer AI"
        )


        # --------------------------------------------------
        # ATTACH PDF
        # --------------------------------------------------

        with pdf_file.open("rb") as file:

            pdf_data = file.read()

        message.add_attachment(
            pdf_data,
            maintype="application",
            subtype="pdf",
            filename="automated_bi_report.pdf",
        )


        # --------------------------------------------------
        # SMTP CONNECTION
        # --------------------------------------------------

        context = ssl.create_default_context()

        smtp_host = settings["smtp_host"]
        smtp_port = settings["smtp_port"]


        with smtplib.SMTP(
            smtp_host,
            smtp_port,
            timeout=30,
        ) as server:

            server.ehlo()

            server.starttls(
                context=context
            )

            server.ehlo()

            # ----------------------------------------------
            # LOGIN
            # ----------------------------------------------

            server.login(
                settings["smtp_username"],
                settings["smtp_password"],
            )

            # ----------------------------------------------
            # SEND
            # ----------------------------------------------

            result = server.send_message(
                message
            )


        # --------------------------------------------------
        # SUCCESS
        # --------------------------------------------------

        if result:

            return (
                False,
                "Brevo accepted the SMTP connection but "
                "reported recipients that were not accepted: "
                f"{result}"
            )


        return (
            True,
            f"Report successfully sent to "
            f"{recipient_email}."
        )


    # ======================================================
    # AUTHENTICATION ERROR
    # ======================================================

    except smtplib.SMTPAuthenticationError as exc:

        return (
            False,
            "❌ Brevo SMTP authentication failed.\n\n"
            "Check:\n"
            "1. SMTP username\n"
            "2. SMTP key\n"
            "3. Brevo SMTP account status\n\n"
            f"Server response: {exc}"
        )


    # ======================================================
    # SENDER ERROR
    # ======================================================

    except smtplib.SMTPSenderRefused as exc:

        return (
            False,
            "❌ Brevo rejected the sender address.\n\n"
            "Make sure the from_email in Streamlit "
            "Secrets is a verified Brevo sender.\n\n"
            f"Server response: {exc}"
        )


    # ======================================================
    # RECIPIENT ERROR
    # ======================================================

    except smtplib.SMTPRecipientsRefused as exc:

        return (
            False,
            "❌ Brevo rejected the recipient email.\n\n"
            f"Recipient response: {exc}"
        )


    # ======================================================
    # DATA ERROR
    # ======================================================

    except smtplib.SMTPDataError as exc:

        return (
            False,
            "❌ Brevo rejected the email message.\n\n"
            f"SMTP response: {exc}"
        )


    # ======================================================
    # CONNECTION ERROR
    # ======================================================

    except smtplib.SMTPConnectError as exc:

        return (
            False,
            "❌ Could not connect to Brevo SMTP.\n\n"
            f"Connection error: {exc}"
        )


    # ======================================================
    # TIMEOUT
    # ======================================================

    except TimeoutError:

        return (
            False,
            "❌ Connection to Brevo timed out."
        )


    # ======================================================
    # SMTP ERROR
    # ======================================================

    except smtplib.SMTPException as exc:

        return (
            False,
            f"❌ Brevo SMTP error:\n{exc}"
        )


    # ======================================================
    # OTHER ERROR
    # ======================================================

    except Exception as exc:

        return (
            False,
            f"❌ Email sending failed:\n{exc}"
        )