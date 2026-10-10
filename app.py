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
import secrets
import sqlite3
from datetime import datetime, timedelta, timezone

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
    """Build the dashboard URL on the same Streamlit application origin."""
    base = _get_app_base_url()
    return base.rstrip("/") + "/?page=dashboard"
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

from modules.dashboard_engine import (
    generate_sheet_templates
)

from modules.chart_engine import (
    create_chart
)

from modules.insight_engine import (
    generate_insights
)

from modules.recommendation_engine import (
    generate_recommendations
)
