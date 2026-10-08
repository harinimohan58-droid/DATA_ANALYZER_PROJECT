import re
import uuid
from pathlib import Path

import requests
import streamlit as st


def get_supabase_settings():
    try:
        section = st.secrets.get("supabase", {})
        url = str(section.get("url", "")).strip().rstrip("/")
        key = str(section.get("anon_key", "")).strip()
        bucket = str(section.get("avatar_bucket", "avatars")).strip() or "avatars"
        if not url or not key:
            return None
        return {"url": url, "anon_key": key, "avatar_bucket": bucket}
    except Exception:
        return None


def _headers(access_token=None):
    settings = get_supabase_settings()
    if not settings:
        return None
    headers = {
        "apikey": settings["anon_key"],
        "Content-Type": "application/json",
    }
    if access_token:
        headers["Authorization"] = f"Bearer {access_token}"
    return headers


def _error_message(response):
    try:
        data = response.json()
        return data.get("msg") or data.get("message") or data.get("error_description") or data.get("error") or response.text
    except Exception:
        return response.text or f"Request failed with HTTP {response.status_code}."


def _valid_email(email):
    return bool(re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", email or ""))


def sign_up_user(email, password, full_name):
    settings = get_supabase_settings()
    if not settings:
        return False, "Supabase authentication is not configured."
    if not _valid_email(email):
        return False, "Please enter a valid email address."

    try:
        response = requests.post(
            f"{settings['url']}/auth/v1/signup",
            headers=_headers(),
            json={
                "email": email,
                "password": password,
                "data": {"full_name": full_name},
            },
            timeout=30,
        )
        if response.status_code not in (200, 201):
            return False, _error_message(response)

        data = response.json()
        user = data.get("user") or {}
        user_id = user.get("id")
        access_token = data.get("access_token", "")

        if not user_id:
            return False, "Supabase did not return a user ID. Check your Supabase Auth settings."

        return True, {
            "user_id": user_id,
            "email": user.get("email", email),
            "name": full_name,
            "access_token": access_token,
        }
    except requests.RequestException as exc:
        return False, f"Could not connect to Supabase: {exc}"


def sign_in_user(email, password):
    settings = get_supabase_settings()
    if not settings:
        return False, "Supabase authentication is not configured."

    try:
        response = requests.post(
            f"{settings['url']}/auth/v1/token?grant_type=password",
            headers=_headers(),
            json={"email": email, "password": password},
            timeout=30,
        )
        if response.status_code != 200:
            return False, _error_message(response)

        data = response.json()
        user = data.get("user") or {}
        user_id = user.get("id")
        access_token = data.get("access_token", "")

        if not user_id or not access_token:
            return False, "Login response did not contain a valid session."

        profile = get_profile(user_id, access_token) or {}
        return True, {
            "user_id": user_id,
            "email": user.get("email", email),
            "name": profile.get("full_name") or user.get("user_metadata", {}).get("full_name", "User"),
            "photo_url": profile.get("photo_url", ""),
            "access_token": access_token,
        }
    except requests.RequestException as exc:
        return False, f"Could not connect to Supabase: {exc}"


def upload_profile_photo(user_id, access_token, uploaded_file):
    settings = get_supabase_settings()
    if not settings:
        return False, "Supabase is not configured."
    if not uploaded_file:
        return False, "Please upload a profile photo."

    try:
        raw = uploaded_file.getvalue()
        if len(raw) > 5 * 1024 * 1024:
            return False, "Profile photo must be 5 MB or smaller."

        suffix = Path(uploaded_file.name).suffix.lower() or ".jpg"
        object_name = f"{user_id}/{uuid.uuid4().hex}{suffix}"
        content_type = uploaded_file.type or "image/jpeg"

        headers = {
            "apikey": settings["anon_key"],
            "Authorization": f"Bearer {access_token}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }

        response = requests.post(
            f"{settings['url']}/storage/v1/object/{settings['avatar_bucket']}/{object_name}",
            headers=headers,
            data=raw,
            timeout=60,
        )
        if response.status_code not in (200, 201):
            return False, _error_message(response)

        public_url = (
            f"{settings['url']}/storage/v1/object/public/"
            f"{settings['avatar_bucket']}/{object_name}"
        )

        profile_headers = _headers(access_token)
        profile_headers["Prefer"] = "return=minimal"
        update = requests.patch(
            f"{settings['url']}/rest/v1/profiles?id=eq.{user_id}",
            headers=profile_headers,
            json={"photo_url": public_url},
            timeout=30,
        )

        if update.status_code not in (200, 204):
            return False, _error_message(update)

        return True, public_url
    except requests.RequestException as exc:
        return False, f"Could not upload profile photo: {exc}"


def get_profile(user_id, access_token):
    settings = get_supabase_settings()
    if not settings or not user_id or not access_token:
        return None

    try:
        response = requests.get(
            f"{settings['url']}/rest/v1/profiles",
            headers=_headers(access_token),
            params={"id": f"eq.{user_id}", "select": "id,email,full_name,photo_url"},
            timeout=20,
        )
        if response.status_code != 200:
            return None
        rows = response.json()
        return rows[0] if rows else None
    except requests.RequestException:
        return None


def sign_out_user(access_token):
    settings = get_supabase_settings()
    if not settings or not access_token:
        return
    try:
        requests.post(
            f"{settings['url']}/auth/v1/logout",
            headers=_headers(access_token),
            timeout=15,
        )
    except requests.RequestException:
        pass
