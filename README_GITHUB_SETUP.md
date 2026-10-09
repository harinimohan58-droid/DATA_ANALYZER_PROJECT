# Data Analyzer AI - GitHub / Streamlit Cloud Setup

This package keeps the existing Data Analyzer application and adds:
- Supabase email/password account creation and login
- Full name and profile photo
- Supabase avatar storage
- Logout
- Brevo SMTP PDF report email

## Files to push
Do not upload `.streamlit/secrets.toml`; use Streamlit Cloud Secrets instead.

## Streamlit Cloud Secrets
Copy the contents of `.streamlit/secrets.toml.example` into:
Streamlit Cloud -> App -> Settings -> Secrets
and replace every placeholder with your real value.

## Supabase
1. Create a Supabase project.
2. Enable Email authentication.
3. Create a public Storage bucket named `avatars`.
4. Create the `profiles` table, trigger and storage policies using the SQL supplied in the project setup instructions.
5. Put the Project URL and publishable/anon key in the `[supabase]` section.

## Brevo
1. Verify the sender email in Brevo.
2. Get the Brevo SMTP login and SMTP key.
3. Put them in the `[email]` section.

## Local test
```powershell
python -m py_compile app.py
streamlit run app.py
```

## GitHub
Commit the project files, but never commit real secrets, `.env`, `venv`, `.git`, or `secrets.toml`.
