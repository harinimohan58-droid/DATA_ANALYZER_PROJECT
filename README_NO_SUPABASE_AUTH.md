# Data Analyzer AI - Local Email/Password Authentication

This version keeps the existing large `app.py` and replaces the Supabase authentication gate with local email/password authentication.

## Account flow
1. Open the app.
2. Choose **Create Account**.
3. Enter Full Name, Email ID, Password, Confirm Password, and Profile Photo.
4. The account is stored in `users.json` with a salted PBKDF2 password hash.
5. The photo is stored under `profiles/`.
6. Login with the email and password.
7. Logout from the sidebar.

## Run locally
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m streamlit run app.py
```

## Important
- Supabase is not required for this version.
- `users.json` and profile photos are intentionally ignored by Git.
- For Streamlit Cloud, local JSON/files are not a reliable production database. This version is intended for local/demo use unless a persistent database is added later.
- Brevo SMTP, if configured, remains separate from account authentication.
