
import hashlib
import hmac
import secrets
import sqlite3
import time

from pathlib import Path


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "auth_users.db"
PHOTO_DIR = BASE_DIR / "profile_photos"

OTP_EXPIRY_SECONDS = 600
MAX_OTP_ATTEMPTS = 5


# ============================================================
# DATABASE CONNECTION
# ============================================================

def _connect():
    connection = sqlite3.connect(str(DB_PATH), timeout=20)
    connection.row_factory = sqlite3.Row
    return connection


def _initialize_database():
    PHOTO_DIR.mkdir(parents=True, exist_ok=True)

    with _connect() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                photo_path TEXT
            )
        """)

        connection.execute("""
            CREATE TABLE IF NOT EXISTS password_reset_otps (
                email TEXT PRIMARY KEY,
                otp_hash TEXT NOT NULL,
                expires_at REAL NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 0
            )
        """)


_initialize_database()


# ============================================================
# PASSWORD HASHING
# ============================================================

def _hash_password(password):
    salt = secrets.token_bytes(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        200_000,
    )

    return salt.hex() + "$" + password_hash.hex()


def _verify_password(password, stored_hash):
    try:
        salt_hex, hash_hex = stored_hash.split("$", 1)
        salt = bytes.fromhex(salt_hex)

        calculated_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            200_000,
        )

        return hmac.compare_digest(
            calculated_hash.hex(),
            hash_hex,
        )

    except (ValueError, AttributeError):
        return False


def _valid_email(email):
    email = (email or "").strip()

    return (
        "@" in email
        and "." in email.rsplit("@", 1)[-1]
        and not any(char.isspace() for char in email)
    )


# ============================================================
# CREATE ACCOUNT
# ============================================================

def create_account(
    name,
    email,
    password,
    confirm_password,
    photo,
):
    name = (name or "").strip()
    email = (email or "").strip().lower()
    password = password or ""
    confirm_password = confirm_password or ""

    if not name:
        return False, "Please enter your name."

    if not _valid_email(email):
        return False, "Please enter a valid email address."

    if len(password) < 8:
        return False, "Password must contain at least 8 characters."

    if password != confirm_password:
        return False, "Passwords do not match."

    if photo is None:
        return False, "Please upload a profile photo."

    extension = Path(
        getattr(photo, "name", "profile.jpg")
    ).suffix.lower()

    if extension not in (".jpg", ".jpeg", ".png", ".webp"):
        extension = ".jpg"

    PHOTO_DIR.mkdir(parents=True, exist_ok=True)

    photo_path = PHOTO_DIR / (secrets.token_hex(16) + extension)

    try:
        photo_path.write_bytes(photo.getvalue())

        with _connect() as connection:
            connection.execute("""
                INSERT INTO users (
                    name,
                    email,
                    password_hash,
                    photo_path
                )
                VALUES (?, ?, ?, ?)
            """, (
                name,
                email,
                _hash_password(password),
                str(photo_path),
            ))

        return True, "Account created successfully."

    except sqlite3.IntegrityError:
        photo_path.unlink(missing_ok=True)
        return False, "An account with this email already exists."

    except Exception as exc:
        photo_path.unlink(missing_ok=True)
        return False, f"Account creation failed: {exc}"


# ============================================================
# LOGIN
# ============================================================

def login_user(email, password):
    email = (email or "").strip().lower()
    password = password or ""

    try:
        with _connect() as connection:
            user = connection.execute("""
                SELECT id, name, email, password_hash, photo_path
                FROM users
                WHERE lower(email) = ?
            """, (email,)).fetchone()

        if user is None:
            return False, "Invalid email or password."

        if not _verify_password(
            password,
            user["password_hash"],
        ):
            return False, "Invalid email or password."

        return True, {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "photo_path": user["photo_path"],
        }

    except sqlite3.Error as exc:
        return False, f"Login database error: {exc}"


# ============================================================
# REQUEST LOCAL OTP
# No email or external API is used.
# ============================================================

def request_password_reset_otp(email):
    email = (email or "").strip().lower()

    if not _valid_email(email):
        return False, "Please enter a valid registered email address."

    try:
        with _connect() as connection:
            user = connection.execute("""
                SELECT email
                FROM users
                WHERE lower(email) = ?
            """, (email,)).fetchone()

        if user is None:
            return False, "No account was found for that email."

        otp = f"{secrets.randbelow(1_000_000):06d}"

        otp_hash = hashlib.sha256(
            otp.encode("utf-8")
        ).hexdigest()

        expires_at = time.time() + OTP_EXPIRY_SECONDS

        with _connect() as connection:
            connection.execute("""
                INSERT INTO password_reset_otps (
                    email,
                    otp_hash,
                    expires_at,
                    attempts
                )
                VALUES (?, ?, ?, 0)
                ON CONFLICT(email) DO UPDATE SET
                    otp_hash = excluded.otp_hash,
                    expires_at = excluded.expires_at,
                    attempts = 0
            """, (
                email,
                otp_hash,
                expires_at,
            ))

        # Local testing only. This OTP is displayed in the app,
        # not emailed to the user.
        return True, (
            f"TEST OTP: {otp}\n\n"
            "Enter this code below to reset your password. "
            "It expires in 10 minutes. This is local testing mode; "
            "no email has been sent."
        )

    except sqlite3.Error as exc:
        return False, f"Could not generate OTP: {exc}"


# ============================================================
# VERIFY OTP AND CHANGE PASSWORD
# ============================================================

def reset_password_with_otp(
    email,
    otp,
    new_password,
):
    email = (email or "").strip().lower()
    otp = (otp or "").strip()
    new_password = new_password or ""

    if not _valid_email(email):
        return False, "Please enter a valid email address."

    if len(otp) != 6 or not otp.isdigit():
        return False, "Enter the six-digit OTP."

    if len(new_password) < 8:
        return False, "New password must contain at least 8 characters."

    try:
        with _connect() as connection:
            record = connection.execute("""
                SELECT otp_hash, expires_at, attempts
                FROM password_reset_otps
                WHERE email = ?
            """, (email,)).fetchone()

            if record is None:
                return False, "Request an OTP first."

            if time.time() > record["expires_at"]:
                connection.execute("""
                    DELETE FROM password_reset_otps
                    WHERE email = ?
                """, (email,))

                return False, "OTP expired. Please request a new OTP."

            if record["attempts"] >= MAX_OTP_ATTEMPTS:
                connection.execute("""
                    DELETE FROM password_reset_otps
                    WHERE email = ?
                """, (email,))

                return (
                    False,
                    "Too many incorrect attempts. Request a new OTP.",
                )

            submitted_hash = hashlib.sha256(
                otp.encode("utf-8")
            ).hexdigest()

            if not hmac.compare_digest(
                submitted_hash,
                record["otp_hash"],
            ):
                connection.execute("""
                    UPDATE password_reset_otps
                    SET attempts = attempts + 1
                    WHERE email = ?
                """, (email,))

                return False, "Incorrect OTP. Please try again."

            password_hash = _hash_password(new_password)

            result = connection.execute("""
                UPDATE users
                SET password_hash = ?
                WHERE lower(email) = ?
            """, (
                password_hash,
                email,
            ))

            if result.rowcount == 0:
                return False, "Account not found."

            connection.execute("""
                DELETE FROM password_reset_otps
                WHERE email = ?
            """, (email,))

        return (
            True,
            "Password changed successfully. You can now log in.",
        )

    except sqlite3.Error as exc:
        return False, f"Password reset failed: {exc}"