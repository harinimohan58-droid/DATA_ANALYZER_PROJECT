import os
import re
import html
import urllib.parse
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

import sys
import socket
import subprocess
import pickle
import time
import hashlib
import json
import io
import itertools
import uuid

import streamlit as st
import pandas as pd

# Resolve all shared files relative to this app.py, not the terminal's current
# working directory. This keeps the main page and ?page=dashboard route aligned.
APP_DIR = Path(__file__).resolve().parent
REPORTS_DIR = APP_DIR / "reports"


def _get_app_base_url():
    """Return the current app origin so dashboard links stay on this app."""
    candidates = []
    try:
        candidates.append(str(st.context.url))
    except Exception:
        pass
    candidates.append(os.environ.get("DATA_ANALYZER_BASE_URL", ""))
    candidates.append("http://localhost:8501/")

    for candidate in candidates:
        candidate = (candidate or "").strip()
        if not candidate:
            continue
        try:
            parsed = urllib.parse.urlsplit(candidate)
            if parsed.scheme and parsed.netloc:
                return urllib.parse.urlunsplit(
                    (parsed.scheme, parsed.netloc, parsed.path or "/", "", "")
                )
        except Exception:
            continue
    return "http://localhost:8501/"


def _get_dashboard_url():
    """Build a unique, shareable URL for this session's dashboard snapshot."""
    if not st.session_state.get("dashboard_share_id"):
        st.session_state["dashboard_share_id"] = uuid.uuid4().hex
    share_id = str(st.session_state["dashboard_share_id"])
    base = _get_app_base_url()
    return base.rstrip("/") + "/?page=dashboard&share=" + urllib.parse.quote(share_id)


def _get_dashboard_share_id_from_url():
    """Read and validate the opaque share token from the dashboard URL."""
    try:
        share_id = str(st.query_params.get("share", "")).strip()
    except Exception:
        try:
            params = st.experimental_get_query_params()
            value = params.get("share", [""])
            share_id = str(value[0] if isinstance(value, list) else value).strip()
        except Exception:
            share_id = ""
    # UUID hex tokens contain exactly 32 lowercase hexadecimal characters.
    return share_id if re.fullmatch(r"[0-9a-f]{32}", share_id) else ""
# Optional legacy module: not required because this app uses its built-in Ask Data engine.
from modules.data_loader import (
    load_file,
    convert_date_columns,
    detect_column_types
)

from modules.profiler import (
    get_data_profile,
    get_missing_values,
    get_data_quality_score,
    get_summary_statistics,
    detect_outliers
)

from modules.analytics import (
    calculate_kpis,
    calculate_correlations,
    get_numeric_summary
)
