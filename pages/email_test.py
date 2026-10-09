
import json
import re
import streamlit as st
from pathlib import Path
from urllib.parse import urlencode

st.set_page_config(
    page_title="Email Setup",
    page_icon="📧",
    layout="wide"
)

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_FILE = BASE_DIR / "email_config.json"


# --------------------------------------------------
# EMAIL CONFIGURATION HELPERS
# --------------------------------------------------
def valid_email(email):
    return bool(
        re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email.strip())
    )


def load_config():
    default = {
        "mode": "Individual",
        "team_name": "",
        "members": []
    }

    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if isinstance(data, dict):
                default.update(data)

        except (OSError, json.JSONDecodeError):
            pass

    return default


def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=4)


# --------------------------------------------------
# LOAD CONFIGURATION
# --------------------------------------------------
if "email_config" not in st.session_state:
    st.session_state.email_config = load_config()

config = st.session_state.email_config

st.title("📧 Email & Account Settings")

email_tab, password_tab = st.tabs([
    "Email Setup",
    "Forgot Password"
])


# ==================================================
# TAB 1: EMAIL SETUP
# ==================================================
with email_tab:

    st.subheader("Choose Email Setup")

    mode = st.radio(
        "Email setup type",
        ["Individual", "Team"],
        horizontal=True,
        key="email_setup_mode"
    )

    if mode == "Individual":

        st.subheader("Individual Email")

        with st.form("individual_form"):

            name = st.text_input("Recipient Name")
            email = st.text_input(
                "Email ID",
                placeholder="example@gmail.com"
            )

            save_individual = st.form_submit_button(
                "Save Email Details",
                use_container_width=True
            )

        if save_individual:

            if not name.strip():
                st.error("Please enter a name.")

            elif not valid_email(email):
                st.error("Please enter a valid email address.")

            else:
                updated = {
                    "mode": "Individual",
                    "team_name": "",
                    "members": [{
                        "name": name.strip(),
                        "email": email.strip()
                    }]
                }

                try:
                    save_config(updated)
                    st.session_state.email_config = updated
                    st.success("Email details saved.")
                    st.rerun()

                except OSError as error:
                    st.error(f"Could not save details: {error}")

    else:

        st.subheader("Team Email Setup")

        old_members = config.get("members", [])

        with st.form("team_form"):

            team_name = st.text_input(
                "Team Name",
                value=config.get("team_name", "")
            )

            count = st.number_input(
                "Number of team members",
                min_value=1,
                max_value=50,
                value=max(1, min(len(old_members) or 1, 50))
            )

            members = []

            for i in range(int(count)):

                old_name = (
                    old_members[i].get("name", "")
                    if i < len(old_members) else ""
                )

                old_email = (
                    old_members[i].get("email", "")
                    if i < len(old_members) else ""
                )

                st.markdown(f"**Member {i + 1}**")

                col1, col2 = st.columns(2)

                with col1:
                    member_name = st.text_input(
                        f"Member {i + 1} Name",
                        value=old_name,
                        key=f"member_name_{i}"
                    )

                with col2:
                    member_email = st.text_input(
                        f"Member {i + 1} Email",
                        value=old_email,
                        key=f"member_email_{i}"
                    )

                members.append({
                    "name": member_name.strip(),
                    "email": member_email.strip()
                })

            save_team = st.form_submit_button(
                "Save Team Email IDs",
                use_container_width=True
            )

        if save_team:

            errors = []

            if not team_name.strip():
                errors.append("Enter a team name.")

            seen = set()

            for i, member in enumerate(members, start=1):

                if not member["name"]:
                    errors.append(f"Enter Member {i}'s name.")

                if not valid_email(member["email"]):
                    errors.append(
                        f"Enter a valid email for Member {i}."
                    )

                normalized = member["email"].lower()

                if normalized in seen:
                    errors.append(
                        f"Duplicate email address for Member {i}."
                    )

                seen.add(normalized)

            if errors:
                for error in errors:
                    st.error(error)

            else:
                updated = {
                    "mode": "Team",
                    "team_name": team_name.strip(),
                    "members": members
                }

                try:
                    save_config(updated)
                    st.session_state.email_config = updated
                    st.success("Team email IDs saved.")
                    st.rerun()

                except OSError as error:
                    st.error(f"Could not save details: {error}")

    st.divider()
    st.subheader("Saved Email IDs")

    config = st.session_state.email_config
    members = config.get("members", [])

    if members:

        if config.get("mode") == "Team":
            st.write(f"**Team:** {config.get('team_name', '')}")

        st.dataframe(
            [
                {
                    "Name": m.get("name", ""),
                    "Email ID": m.get("email", "")
                }
                for m in members
            ],
            use_container_width=True,
            hide_index=True
        )

        st.subheader("Prepare Report Email")

        valid_members = [
            m for m in members if valid_email(m.get("email", ""))
        ]

        options = {
            f"{m.get('name', 'Member')} ({m['email']})": m["email"]
            for m in valid_members
        }

        selected = st.multiselect(
            "Select recipients",
            list(options.keys()),
            default=list(options.keys())
        )

        subject = st.text_input(
            "Subject",
            value="Data Analyzer - Final Report"
        )

        body = st.text_area(
            "Message",
            value=(
                "Hello,\n\n"
                "Please find the Data Analyzer report attached.\n\n"
                "Regards"
            )
        )

        if selected:

            recipient_emails = [options[item] for item in selected]

            query = urlencode({
                "view": "cm",
                "fs": "1",
                "to": ",".join(recipient_emails),
                "su": subject,
                "body": body
            })

            st.link_button(
                "📨 Open Gmail",
                "https://mail.google.com/mail/?" + query,
                use_container_width=True
            )

            st.caption(
                "Attach the downloaded PDF manually in Gmail before sending."
            )

    else:
        st.info("No email IDs saved yet.")


# ==================================================
# TAB 2: FORGOT PASSWORD
# ==================================================
with password_tab:

    st.subheader("🔐 Forgot Password")

    st.write(
        "Enter your registered account email to begin password recovery."
    )

    with st.form("forgot_password_form"):

        reset_email = st.text_input(
            "Registered Email ID",
            placeholder="Enter your account email"
        )

        request_reset = st.form_submit_button(
            "Request Password Reset",
            use_container_width=True
        )

    if request_reset:

        if not valid_email(reset_email):
            st.error("Please enter a valid email address.")

        else:
            st.warning(
                "The password-reset interface is restored, but it is not "
                "connected to your account recovery system yet. To enable "
                "real password resets, this page must call the existing "
                "reset function in your auth.py."
            )

            st.info(
                "No password was changed and no reset email was sent."
            )

    st.caption(
        "For security, password recovery should use a time-limited, "
        "single-use reset link rather than emailing a password."
    )