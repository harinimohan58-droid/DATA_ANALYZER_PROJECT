import os
import re
import html
import urllib.parse
import urllib.request
import pickle
from html.parser import HTMLParser
from pathlib import Path
<<<<<<< HEAD

import sys
import socket
import subprocess
import pickle
import time
=======
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572

import streamlit as st
import pandas as pd
from modules.user_demand_engine import render_user_demand_section
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

from modules.web_research import (
    research_dataset,
    get_research_sources
)

from modules.data_context import (
    create_data_context
)



from modules.ai_analyst import (
    ask_data_analyst
)

from modules.report_generator import (
    generate_pdf
)

# ==========================================================
# PROFESSIONAL DATA-DRIVEN BUSINESS QUESTION GENERATOR
# ==========================================================

def _pretty_column_name(column):
    """Turn a dataframe column name into a user-friendly business label."""
    text = re.sub(r"[_\\-]+", " ", str(column)).strip()
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    return text.strip().title()


def _question_column(columns, keywords, excluded=None):
    """Find the most relevant real column using keyword matching."""
    excluded = set(excluded or [])
    candidates = []
    for column in columns:
        if column in excluded:
            continue
        name = str(column).lower().replace("_", " ").replace("-", " ")
        score = sum(1 for keyword in keywords if keyword in name)
        if score:
            candidates.append((score, len(name), column))
    if not candidates:
        return None
    candidates.sort(key=lambda x: (-x[0], x[1]))
    return candidates[0][2]


def _detect_question_domain(df):
    """Use the same data-driven domain classification as the research engine."""
    detected = _detect_business_domain(df) if "_detect_business_domain" in globals() else "General Business Analytics"
    mapping = {
        "Short-Term Lending / Loan Analytics": "Finance / Loan Analytics",
        "Banking / Financial Services": "Finance / Loan Analytics",
        "Insurance Analytics": "Insurance Analytics",
        "Marketing / Campaign Analytics": "Marketing / Customer Analytics",
        "Retail / Sales Analytics": "Retail / Sales Analytics",
        "Manufacturing Analytics": "Manufacturing Analytics",
        "Healthcare Analytics": "Healthcare Analytics",
        "Education Analytics": "Education Analytics",
        "Telecom Analytics": "Telecom / Churn Analytics",
        "Human Resources / Workforce Analytics": "Human Resources / Workforce Analytics",
    }
    return mapping.get(detected, "General Business Analytics")

def generate_data_questions(df):
    """Generate professional, business-oriented questions from the actual schema.

    The questions intentionally avoid generic dataframe questions such as
    record count, column count, average age, or list-all-categories. They are
    built from real columns, business-domain signals, relationships, segments,
    trends, and decision-oriented analysis opportunities in the uploaded data.
    """
    if df is None or df.empty:
        return [
            "What business pattern should be investigated first in this dataset?",
            "Which available customer, product, employee, or transaction segment shows the strongest business signal?",
            "What relationships between the available measures could support a business decision?",
        ]

    columns = list(df.columns)
    numeric = df.select_dtypes(include="number").columns.tolist()
    categorical = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()
    dates = df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns.tolist()
    domain = _detect_question_domain(df)

    questions = []

    # -----------------------------
    # Identify useful business fields
    # -----------------------------
    income = _question_column(columns, ["income", "salary", "revenue", "sales", "amount", "balance"])
    outcome = _question_column(columns, [
        "loan", "account", "attrition", "churn", "default", "fraud",
        "response", "conversion", "purchase", "profit", "sales", "revenue"
    ])
    customer = _question_column(columns, ["customer", "client", "member", "account holder"])
    product = _question_column(columns, ["product", "item", "category", "service"])
    geography = _question_column(columns, ["region", "city", "state", "country", "location", "branch", "territory"])
    demographic = _question_column(columns, ["age", "gender", "marital", "qualification", "education"])
    department = _question_column(columns, ["department", "job role", "jobrole", "team", "division"])
    time_col = dates[0] if dates else _question_column(columns, ["date", "year", "month", "quarter", "week"])

<<<<<<< HEAD
    # High-cardinality identifiers are generally not useful as business dimensions.
    categorical_business = [
        c for c in categorical
        if df[c].nunique(dropna=True) <= max(2, min(100, len(df) * 0.25))
=======
    numeric_columns = (
        df.select_dtypes(include="number")
        .columns
        .tolist()
    )

    categorical_columns = (
        df.select_dtypes(
            include=["object", "category", "bool"]
        )
        .columns
        .tolist()
    )

    # ------------------------------------------------------
    # DATASET OVERVIEW
    # ------------------------------------------------------

    questions.append(
        f"What are the main characteristics of this dataset?"
    )

    questions.append(
        f"Which columns contain the most useful information "
        f"for analysis?"
    )

    # ------------------------------------------------------
    # CATEGORICAL DATA
    # ------------------------------------------------------

    for column in categorical_columns[:3]:

        questions.append(
            f"What are the most common groups in {column}?"
        )

        if numeric_columns:

            metric = numeric_columns[0]

            questions.append(
                f"How does {metric} vary across {column}?"
            )

    # ------------------------------------------------------
    # NUMERIC DATA
    # ------------------------------------------------------

    for column in numeric_columns[:3]:

        questions.append(
            f"What is the overall pattern of {column}?"
        )

    # ------------------------------------------------------
    # RELATIONSHIPS BETWEEN NUMERIC VARIABLES
    # ------------------------------------------------------

    if len(numeric_columns) >= 2:

        x = numeric_columns[0]
        y = numeric_columns[1]

        questions.append(
            f"Is there a relationship between {x} and {y}?"
        )

    # ------------------------------------------------------
    # DATA QUALITY
    # ------------------------------------------------------

    missing_columns = [
        column
        for column in columns
        if df[column].isna().sum() > 0
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572
    ]

    # -----------------------------
    # Domain-specific questions
    # -----------------------------
    if domain == "Finance / Loan Analytics":
        if outcome and income:
            questions.append(
                f"How does {_pretty_column_name(outcome)} participation vary across {_pretty_column_name(income)} levels?"
            )
        if outcome and demographic:
            questions.append(
                f"Which {_pretty_column_name(demographic)} segments show the highest concentration of {_pretty_column_name(outcome)}?"
            )
        if income and demographic:
            questions.append(
                f"How does {_pretty_column_name(income)} differ across {_pretty_column_name(demographic)} groups?"
            )
        if outcome:
            questions.append(
                f"Which customer characteristics distinguish records with and without {_pretty_column_name(outcome)}?"
            )
        if geography and outcome:
            questions.append(
                f"Which {_pretty_column_name(geography)} segments have the highest concentration of {_pretty_column_name(outcome)}?"
            )
        if income and categorical_business:
            c = categorical_business[0]
            if c not in {outcome, demographic, geography}:
                questions.append(
                    f"Which {_pretty_column_name(c)} groups have the highest average {_pretty_column_name(income)}?"
                )
        questions.extend([
            "Which customer segments appear most relevant for further financial-product analysis?",
            "Are there customer groups with relatively strong financial characteristics but comparatively low product participation?",
            "What combination of demographic and financial characteristics should be investigated for customer segmentation?",
        ])

    elif domain == "Human Resources / Workforce Analytics":
        attrition = _question_column(columns, ["attrition", "left", "turnover", "exit"])
        salary = _question_column(columns, ["salary", "income", "compensation", "wage"])
        satisfaction = _question_column(columns, ["satisfaction", "engagement", "environment"])
        if attrition and department:
            questions.append(
                f"Which {_pretty_column_name(department)} groups show the highest concentration of {_pretty_column_name(attrition)}?"
            )
        if attrition and salary:
            questions.append(
                f"How does {_pretty_column_name(attrition)} vary across {_pretty_column_name(salary)} levels?"
            )
        if attrition and satisfaction:
            questions.append(
                f"What relationship exists between {_pretty_column_name(satisfaction)} and {_pretty_column_name(attrition)}?"
            )
        if department and salary:
            questions.append(
                f"Which {_pretty_column_name(department)} groups have the highest average {_pretty_column_name(salary)}?"
            )
        questions.extend([
            "Which employee segments should be investigated further for retention or workforce-planning decisions?",
            "What employee characteristics are most strongly associated with the key workforce outcome in this dataset?",
            "Which workforce groups show patterns that may require management attention?",
        ])

    elif domain == "Marketing / Customer Analytics":
        conversion = _question_column(columns, ["conversion", "response", "purchase", "converted"])
        campaign = _question_column(columns, ["campaign", "channel", "source", "medium"])
        if campaign and conversion:
            questions.append(
                f"Which {_pretty_column_name(campaign)} groups are associated with the strongest {_pretty_column_name(conversion)} performance?"
            )
        if customer and conversion:
            questions.append(
                f"Which customer characteristics are associated with {_pretty_column_name(conversion)}?"
            )
        if income and conversion:
            questions.append(
                f"How does {_pretty_column_name(conversion)} vary across {_pretty_column_name(income)} levels?"
            )
        questions.extend([
            "Which customer segments should be investigated for targeted campaign opportunities?",
            "Which marketing or customer attributes appear most relevant to the observed response or conversion outcome?",
            "Are there customer groups with strong engagement but comparatively weak conversion that require further investigation?",
        ])

    elif domain == "Retail / Sales Analytics":
        metric = _question_column(columns, ["sales", "revenue", "profit", "amount"])
        if product and metric:
            questions.append(
                f"Which {_pretty_column_name(product)} groups contribute the most {_pretty_column_name(metric)}?"
            )
        if geography and metric:
            questions.append(
                f"Which {_pretty_column_name(geography)} areas contribute most to {_pretty_column_name(metric)}?"
            )
        if time_col and metric:
            questions.append(
                f"What trend is visible in {_pretty_column_name(metric)} over {_pretty_column_name(time_col)}?"
            )
        if customer and metric:
            questions.append(
                f"Which customer segments contribute the highest {_pretty_column_name(metric)}?"
            )
        questions.extend([
            "Which products or customer segments should be investigated for growth opportunities?",
            "Where are the strongest and weakest business-performance patterns across the available sales dimensions?",
            "Which segments show high activity but comparatively weak financial performance?",
        ])

    elif domain == "Healthcare Analytics":
        outcome_health = _question_column(columns, ["diagnosis", "treatment", "outcome", "readmission", "discharge"])
        if outcome_health and demographic:
            questions.append(
                f"How does {_pretty_column_name(outcome_health)} vary across {_pretty_column_name(demographic)} groups?"
            )
        if outcome_health and geography:
            questions.append(
                f"Which {_pretty_column_name(geography)} groups show the strongest concentration of {_pretty_column_name(outcome_health)}?"
            )
        questions.extend([
            "Which patient segments show patterns that require further clinical or operational investigation?",
            "What demographic or service-related characteristics are associated with the observed patient outcomes?",
        ])

    elif domain == "Education Analytics":
        score = _question_column(columns, ["score", "marks", "grade", "result", "percentage"])
        attendance = _question_column(columns, ["attendance", "absence", "present"])
        if score and attendance:
            questions.append(
                f"What relationship exists between {_pretty_column_name(attendance)} and {_pretty_column_name(score)}?"
            )
        if score and demographic:
            questions.append(
                f"How does {_pretty_column_name(score)} vary across {_pretty_column_name(demographic)} groups?"
            )
        questions.extend([
            "Which student segments show patterns that require academic support or further investigation?",
            "Which available factors are most closely associated with student performance?",
        ])

    elif domain == "Manufacturing Analytics":
        defect = _question_column(columns, ["defect", "failure", "quality", "rejection"])
        machine = _question_column(columns, ["machine", "line", "equipment", "plant"])
        if defect and machine:
            questions.append(
                f"Which {_pretty_column_name(machine)} groups have the highest concentration of {_pretty_column_name(defect)}?"
            )
        if defect and numeric:
            metric = next((c for c in numeric if c != defect), None)
            if metric:
                questions.append(
                    f"How does {_pretty_column_name(defect)} vary with {_pretty_column_name(metric)}?"
                )
        questions.extend([
            "Which production segments should be investigated for quality or operational improvement?",
            "Which available operating factors are most associated with the observed quality outcome?",
        ])

    elif domain == "Telecom / Churn Analytics":
        churn = _question_column(columns, ["churn", "attrition", "left"])
        tenure = _question_column(columns, ["tenure", "months", "duration"])
        contract = _question_column(columns, ["contract", "plan", "service"])
        if churn and tenure:
            questions.append(
                f"How does {_pretty_column_name(churn)} vary across {_pretty_column_name(tenure)} levels?"
            )
        if churn and contract:
            questions.append(
                f"Which {_pretty_column_name(contract)} groups show the highest concentration of {_pretty_column_name(churn)}?"
            )
        questions.extend([
            "Which customer segments should be investigated for retention opportunities?",
            "What customer characteristics are most associated with the observed churn pattern?",
        ])

    # -----------------------------
    # Universal relationship questions
    # -----------------------------
    if len(numeric) >= 2:
        questions.append(
            f"What relationship exists between {_pretty_column_name(numeric[0])} and {_pretty_column_name(numeric[1])}, and why might it matter for the business?"
        )

<<<<<<< HEAD
    if categorical_business and numeric:
        c = categorical_business[0]
        m = numeric[0]
=======
    # ------------------------------------------------------
    # DUPLICATES
    # ------------------------------------------------------

    if df.duplicated().sum() > 0:

>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572
        questions.append(
            f"Which {_pretty_column_name(c)} segments have the highest average {_pretty_column_name(m)}?"
        )

<<<<<<< HEAD
    if time_col and numeric:
        m = numeric[0]
        questions.append(
            f"What important trend or change is visible in {_pretty_column_name(m)} over {_pretty_column_name(time_col)}?"
        )
=======
    # ------------------------------------------------------
    # REMOVE DUPLICATES
    # ------------------------------------------------------

    cleaned_questions = []
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572

    # Add a data-quality/business-risk question only when the data actually has an issue.
    if int(df.isna().sum().sum()) > 0:
        questions.append(
            "Which missing-data areas could affect the reliability of the business analysis?"
        )

    if int(df.duplicated().sum()) > 0:
        questions.append(
            "Could duplicate records materially affect the business metrics or segment analysis?"
        )

    # Final fallback for unusual datasets.
    if not questions:
        questions = [
            "Which available business dimension shows the strongest difference in the main numeric measures?",
            "What relationships between the available fields could explain an important business pattern?",
            "Which segment or group should be investigated further based on the observed data?",
        ]

    # Remove duplicates while preserving the order of business relevance.
    cleaned = []
    seen = set()
    for question in questions:
        q = re.sub(r"\\s+", " ", question).strip()
        key = q.lower()
        if q and key not in seen:
            seen.add(key)
            cleaned.append(q)

    return cleaned[:16]

# ==========================================================
# ONLINE BASIC DATA EXPLANATION
# ==========================================================

class _SearchResultParser(HTMLParser):
    """Small dependency-free parser for DuckDuckGo HTML results."""

    def __init__(self):
        super().__init__()
        self.results = []
        self._current = None
        self._capture_title = False
        self._capture_snippet = False
        self._title_parts = []
        self._snippet_parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "")
        if tag == "a" and "result__a" in classes:
            self._capture_title = True
            self._title_parts = []
            self._current = {
                "title": "",
                "url": attrs.get("href", "")
            }
        elif tag in ("a", "div") and "result__snippet" in classes:
            self._capture_snippet = True
            self._snippet_parts = []

    def handle_data(self, data):
        if self._capture_title:
            self._title_parts.append(data)
        if self._capture_snippet:
            self._snippet_parts.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._capture_title:
            self._capture_title = False
            if self._current is not None:
                self._current["title"] = " ".join(self._title_parts).strip()
        if self._capture_snippet and tag in ("a", "div"):
            self._capture_snippet = False
            if self._current is not None:
                self._current["snippet"] = " ".join(self._snippet_parts).strip()
                if self._current.get("title"):
                    self.results.append(self._current)
                self._current = None


def _clean_text(value):
    value = html.unescape(str(value or ""))
    return re.sub(r"\s+", " ", value).strip()


def _search_web(query, max_results=5):
    """Run a lightweight public web search without requiring an API key."""
    try:
        encoded = urllib.parse.urlencode({"q": query})
        url = f"https://html.duckduckgo.com/html/?{encoded}"
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(request, timeout=8) as response:
            content = response.read().decode("utf-8", errors="ignore")

        parser = _SearchResultParser()
        parser.feed(content)

        cleaned = []
        seen = set()
        for item in parser.results:
            title = _clean_text(item.get("title"))
            snippet = _clean_text(item.get("snippet"))
            raw_url = item.get("url", "")

            # DuckDuckGo may return a redirect URL.
            match = re.search(r"uddg=([^&]+)", raw_url)
            if match:
                raw_url = urllib.parse.unquote(match.group(1))

            if not raw_url.startswith("http"):
                continue

            key = raw_url.split("#")[0]
            if key in seen:
                continue
            seen.add(key)

            cleaned.append({
                "title": title or "Web source",
                "url": raw_url,
                "snippet": snippet
            })

            if len(cleaned) >= max_results:
                break

        return cleaned

    except Exception:
        return []


def _detect_business_domain(df):
<<<<<<< HEAD
    """Detect the business domain from specific combinations of real fields.

    Generic fields such as Income, Amount, Customer or Status are deliberately
    given little/no weight by themselves so unrelated datasets are not
    incorrectly classified as HR or finance.
    """
    names = {_bi_norm(c) for c in df.columns}
    joined = " | ".join(sorted(names))

    signatures = {
        "Short-Term Lending / Loan Analytics": [
            ("loan amount", 7), ("interest rate", 7), ("credit score", 7),
            ("loan status", 7), ("loan term", 6), ("emi", 6),
            ("repayment", 5), ("borrower", 5), ("default", 5), ("loan", 4),
        ],
        "Banking / Financial Services": [
            ("account number", 6), ("account", 4), ("transaction", 5),
            ("deposit", 5), ("withdrawal", 5), ("balance", 4),
            ("bank", 4), ("payment", 3),
        ],
        "Insurance Analytics": [
            ("policy number", 6), ("policy", 5), ("premium", 5),
            ("claim", 5), ("coverage", 5), ("insurance", 5),
        ],
        "Marketing / Campaign Analytics": [
            ("campaign", 6), ("conversion", 6), ("click", 5),
            ("impression", 5), ("lead", 5), ("response", 4),
            ("channel", 3), ("marketing", 5),
        ],
        "Retail / Sales Analytics": [
            ("retail sales", 7), ("warehouse sales", 7), ("retail transfers", 7),
            ("revenue", 5), ("sales", 4), ("product", 3), ("quantity", 3),
            ("order", 3), ("profit", 4),
        ],
        "Manufacturing Analytics": [
            ("machine", 6), ("production", 6), ("defect", 6),
            ("maintenance", 5), ("downtime", 5), ("quality", 4),
            ("temperature", 4), ("pressure", 4),
        ],
        "Healthcare Analytics": [
            ("patient", 6), ("diagnosis", 6), ("hospital", 6),
            ("admission", 5), ("discharge", 5), ("treatment", 5),
            ("disease", 5), ("medical", 5),
        ],
        "Education Analytics": [
            ("student", 6), ("grade", 5), ("marks", 5),
            ("attendance", 5), ("course", 4), ("exam", 4),
            ("education", 5),
        ],
        "Telecom Analytics": [
            ("churn", 6), ("contract", 5), ("internet service", 5),
            ("monthly charges", 5), ("phone service", 5), ("tenure", 3),
        ],
        "Human Resources / Workforce Analytics": [
            ("employee", 7), ("attrition", 7), ("job role", 6),
            ("years at company", 7), ("monthly income", 6), ("overtime", 5),
            ("employee number", 7), ("hire date", 6),
        ],
    }

    scored = []
    for domain, rules in signatures.items():
        score = 0
        matched = []
        for phrase, weight in rules:
            p = _bi_norm(phrase)
            if p in names or p in joined:
                score += weight
                matched.append(p)
        scored.append((score, len(matched), domain, matched))

    scored.sort(reverse=True)
    if not scored or scored[0][0] < 6:
        return "General Business Analytics"

    top = scored[0]
    second = scored[1] if len(scored) > 1 else (0, 0, "", [])
    # Require a meaningful lead where multiple domains have signals.
    if top[0] >= 7 and (top[0] - second[0] >= 2 or top[1] >= 2):
        return top[2]
=======
    """Identify a likely business domain from column names only."""
    names = " ".join(str(c).lower() for c in df.columns)

    domain_rules = [
        ("Retail / Sales Analytics", [
            "retail sales", "retail transfers", "warehouse sales",
            "product", "item", "sales", "quantity", "order"
        ]),
        ("Human Resources / Workforce Analytics", [
            "employee", "attrition", "jobrole", "job role", "department",
            "salary", "monthlyincome", "overtime", "satisfaction"
        ]),
        ("Marketing / Campaign Analytics", [
            "campaign", "marketing", "conversion", "response",
            "click", "impression", "lead", "customer"
        ]),
        ("Finance / Risk Analytics", [
            "loan", "credit", "default", "transaction", "fraud",
            "balance", "interest", "risk", "amount"
        ]),
        ("Healthcare Analytics", [
            "patient", "diagnosis", "hospital", "admission", "discharge",
            "medical", "treatment", "disease"
        ]),
        ("Education Analytics", [
            "student", "grade", "marks", "score", "attendance",
            "course", "exam", "education"
        ]),
        ("Manufacturing Analytics", [
            "machine", "defect", "production", "maintenance", "downtime",
            "quality", "temperature", "pressure"
        ]),
        ("Telecom Analytics", [
            "churn", "tenure", "contract", "internet", "telecom",
            "monthlycharges", "phone service"
        ]),
    ]

    best_domain = "General Business Analytics"
    best_score = 0
    for domain, keywords in domain_rules:
        score = sum(1 for keyword in keywords if keyword in names)
        if score > best_score:
            best_domain = domain
            best_score = score

    return best_domain
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572

    return top[2] if top[0] >= 10 else "General Business Analytics"

def _column_local_explanation(column, dtype):
    """Safe explanation when an exact online definition is not found."""
    name = str(column)
    n = name.lower().replace("_", " ").strip()

    known = {
        "year": "Calendar year associated with the record.",
        "month": "Month associated with the record.",
        "supplier": "Supplier or vendor associated with the product or record.",
        "item code": "Identifier used to distinguish a product/item.",
        "item description": "Text description or name of the product/item.",
        "item type": "Category or type assigned to the product/item.",
        "retail sales": "Retail sales quantity/value recorded for the product, depending on the dataset's unit definition.",
        "retail transfers": "Quantity/value associated with transfers to retail locations or operations, depending on the source definition.",
        "warehouse sales": "Sales quantity/value associated with warehouse operations, depending on the source definition.",
        "product": "Product or item associated with the record.",
        "quantity": "Number of units/items associated with the record.",
        "sales": "Sales measure recorded for the transaction, product, period, or business unit.",
        "revenue": "Revenue or monetary sales amount associated with the record.",
        "price": "Price or monetary amount associated with the product or transaction.",
        "customer": "Customer identifier or customer-related information.",
        "order date": "Date on which the order was placed.",
    }

    if n in known:
        return known[n]

    if dtype.startswith("datetime"):
        return "Date/time field that can be used for time-based analysis and trends."
    if dtype.startswith("int") or dtype.startswith("float"):
        return "Numeric field that can be summarized, compared, grouped, or used as a business metric."
    if dtype == "bool":
        return "Boolean field representing a true/false or yes/no condition."
    return "Categorical/text field that can be used to group, filter, compare, or describe records."


def generate_basic_data_explanation(df):
    """Research the uploaded dataset/domain online and explain the actual data."""
    domain = _detect_business_domain(df)
    columns = list(df.columns)
    column_text = ", ".join(str(c) for c in columns[:12])

    # Strong signature searches are used first so well-known public datasets
    # can be matched to their original documentation.
    queries = []
    names_lower = " ".join(str(c).lower() for c in columns)

    if all(x in names_lower for x in ["retail sales", "retail transfers", "warehouse sales"]):
        queries.append(
            '"RETAIL SALES" "RETAIL TRANSFERS" "WAREHOUSE SALES" dataset'
        )

<<<<<<< HEAD
    queries.append(
        f'"{domain}" dataset column definitions {column_text}'
    )

    research_terms = {
        "Short-Term Lending / Loan Analytics": "loan approval credit risk repayment default interest rate",
        "Banking / Financial Services": "banking transaction account balance payment risk analytics",
        "Insurance Analytics": "insurance policy premium claims coverage risk analytics",
        "Marketing / Campaign Analytics": "campaign conversion customer response channel marketing analytics",
        "Retail / Sales Analytics": "sales revenue product demand inventory retail analytics",
        "Manufacturing Analytics": "production quality defects machine downtime manufacturing analytics",
        "Healthcare Analytics": "patient treatment diagnosis hospital healthcare analytics",
        "Education Analytics": "student performance attendance grades education analytics",
        "Telecom Analytics": "customer churn telecom contract service analytics",
        "Human Resources / Workforce Analytics": "employee attrition workforce job role retention analytics",
    }.get(domain, "business performance analytics trends segmentation")

    queries.append(
        f'{domain} data analytics business uses {research_terms}'
    )
=======
    queries.append(f'"{domain}" dataset column definitions {column_text}')
    queries.append(f'{domain} data analytics business uses sales product performance inventory')
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572

    all_results = []
    seen_urls = set()
    for query in queries:
        for result in _search_web(query, max_results=5):
            if result["url"] not in seen_urls:
                seen_urls.add(result["url"])
                all_results.append(result)
            if len(all_results) >= 10:
                break
        if len(all_results) >= 10:
            break

    # Build online evidence from the returned snippets.
    online_text = []
    for result in all_results[:5]:
        if result.get("snippet"):
            online_text.append(result["snippet"])

    exact_source_match = None
    if all(x in names_lower for x in ["retail sales", "retail transfers", "warehouse sales"]):
        for result in all_results:
            text = (result.get("title", "") + " " + result.get("snippet", "")).lower()
            if "warehouse and retail sales" in text or "montgomery" in text:
                exact_source_match = result
                break

    if exact_source_match:
        dataset_description = (
            "The uploaded columns closely match the publicly documented "
            "Warehouse and Retail Sales dataset structure. The published "
            "documentation describes sales and movement data by item and "
            "department, with fields such as supplier, item code, item type, "
            "retail sales, retail transfers and warehouse sales. "
            "The exact meaning and unit should still be treated according "
            "to the identified source documentation."
        )
    else:
        dataset_description = (
            f"The uploaded file appears to be a {domain.lower()} dataset "
            f"with {len(df):,} records and {len(columns)} columns. "
            "The explanation below combines the actual structure of the "
            "uploaded file with publicly available information found online. "
            "Where an exact source definition could not be verified, the app "
            "labels the meaning as an interpretation rather than a confirmed definition."
        )

    business_uses = []
    domain_lower = domain.lower()
    if "retail" in domain_lower:
        business_uses = [
            "Product and sales performance monitoring",
            "Demand and inventory planning",
            "Product/category comparison",
            "Sales trend and seasonal analysis",
            "Merchandising, pricing and promotion decisions",
        ]
    elif "human resources" in domain_lower:
        business_uses = [
            "Workforce and employee trend analysis",
            "Attrition and retention monitoring",
            "Department and job-role comparison",
            "Workforce planning",
            "Employee experience analysis",
        ]
    elif "marketing" in domain_lower:
        business_uses = [
            "Campaign performance analysis",
            "Customer response and conversion analysis",
            "Audience segmentation",
            "Channel comparison",
            "Marketing performance monitoring",
        ]
<<<<<<< HEAD

    elif "loan" in domain_lower:

        business_uses = [
            "Loan portfolio and approval analysis",
            "Borrower segment comparison",
            "Credit and repayment pattern analysis",
            "Interest-rate and loan-term analysis",
            "Default / risk monitoring",
        ]

    elif "banking" in domain_lower or "financial" in domain_lower:

        business_uses = [
            "Transaction and account activity analysis",
            "Balance and payment behaviour analysis",
            "Customer/account segmentation",
            "Financial risk monitoring",
            "Exception and anomaly investigation",
        ]

    elif "insurance" in domain_lower:

        business_uses = [
            "Policy and premium analysis",
            "Claims pattern analysis",
            "Customer and coverage segmentation",
            "Loss/risk monitoring",
            "Portfolio performance analysis",
        ]

=======
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572
    else:
        business_uses = [
            "Business performance monitoring",
            "Trend and group comparison",
            "Data quality monitoring",
            "Identification of important business patterns",
            "Decision support and further investigation",
        ]

    column_rows = []
    for column in columns:
        dtype = str(df[column].dtype)
        exact_match = None
        normalized = str(column).lower().replace("_", " ").strip()

        # Use online snippets only when they clearly contain the column name.
        for result in all_results:
            blob = (result.get("title", "") + " " + result.get("snippet", "")).lower()
            if normalized and normalized in blob and len(normalized) >= 4:
                snippet = result.get("snippet", "")
                if snippet:
                    exact_match = snippet
                    break

        explanation = exact_match if exact_match else _column_local_explanation(column, dtype)
        column_rows.append({
            "Column": column,
            "Data Type": dtype,
            "Meaning / Explanation": explanation,
            "Missing Values": int(df[column].isna().sum()),
            "Unique Values": int(df[column].nunique(dropna=True)),
        })

    return {
        "domain": domain,
        "dataset_description": dataset_description,
        "business_uses": business_uses,
        "column_rows": column_rows,
        "online_evidence": online_text,
        "sources": all_results[:10],
        "research_status": "Online research completed" if all_results else "Online research unavailable; local structural explanation used",
    }



<<<<<<< HEAD
# ==========================================================
# DATA-DRIVEN BUSINESS INSIGHT ENGINE
# ==========================================================

def _bi_norm(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()


def _bi_pretty(value):
    return re.sub(r"\s+", " ", re.sub(r"[_-]+", " ", str(value))).strip().title()


def _bi_fmt(value):
    try:
        value = float(value)
        if abs(value) >= 1_000_000:
            return f"{value/1_000_000:.2f}M"
        if abs(value) >= 1_000:
            return f"{value:,.0f}"
        return f"{value:,.2f}"
    except Exception:
        return str(value)


# Consistent professional palette used by both dashboard views.
# The palette is applied to generated charts so the dashboard is
# colourful without changing the user's chart layout or interactions.
DASHBOARD_PALETTE = [
    "#22D3EE", "#3B82F6", "#8B5CF6", "#EC4899", "#FB923C",
    "#34D399", "#FBBF24", "#60A5FA", "#A78BFA", "#F472B6",
    "#2DD4BF", "#FB7185"
]


def _apply_dashboard_palette(sheets):
    """Assign attractive, different chart colours while preserving order."""
    for sheet_index, sheet in enumerate(sheets or []):
        for chart_index, chart in enumerate(sheet.get("charts", [])):
            chart["color"] = DASHBOARD_PALETTE[
                (sheet_index * 5 + chart_index) % len(DASHBOARD_PALETTE)
            ]
    return sheets


def _style_neon_figure(fig, chart=None):
    """Apply the supplied reference's midnight-blue/neon visual language to Plotly charts."""
    try:
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(7,18,40,0.72)",
            font=dict(
                family="Inter, Segoe UI, sans-serif",
                color="#DCEBFF",
                size=12,
            ),
            title=dict(
                font=dict(
                    color="#F6FAFF",
                    size=17,
                ),
                x=0.02,
                xanchor="left",
            ),
            margin=dict(l=42, r=24, t=62, b=44),
            hoverlabel=dict(
                bgcolor="#0A1730",
                bordercolor="#2B5B91",
                font=dict(color="#F7FAFF", size=12),
            ),
            legend=dict(
                font=dict(color="#AFC3DF", size=11),
                bgcolor="rgba(0,0,0,0)",
            ),
            xaxis=dict(
                color="#90A9CA",
                gridcolor="rgba(55,91,145,.28)",
                linecolor="rgba(77,113,169,.35)",
                zerolinecolor="rgba(77,113,169,.25)",
                title_font=dict(color="#8EA9CA"),
            ),
            yaxis=dict(
                color="#90A9CA",
                gridcolor="rgba(55,91,145,.28)",
                linecolor="rgba(77,113,169,.35)",
                zerolinecolor="rgba(77,113,169,.25)",
                title_font=dict(color="#8EA9CA"),
            ),
        )

        # Give pie/donut charts the same multi-neon visual language as the reference.
        if chart and str(chart.get("chart_type", "")).lower() == "pie":
            neon = [
                "#22D3EE", "#8B5CF6", "#EC4899", "#FB923C",
                "#34D399", "#3B82F6", "#FBBF24", "#F472B6"
            ]
            for trace in fig.data:
                if hasattr(trace, "marker") and trace.marker is not None:
                    try:
                        trace.marker.colors = neon
                    except Exception:
                        pass

        # Slight glow-like line treatment.
        for trace in fig.data:
            try:
                if getattr(trace, "mode", None) and "lines" in str(trace.mode):
                    trace.line.width = 3
            except Exception:
                pass

    except Exception:
        pass

    return fig


def build_business_insights(df, sheets=None):
    """Generate insights only from fields that actually exist in the uploaded data."""
    rows = []
    n = max(len(df), 1)

    missing = int(df.isna().sum().sum())
    duplicates = int(df.duplicated().sum())

    if missing:
        affected = int((df.isna().sum() > 0).sum())
        pct = missing / (len(df) * max(len(df.columns), 1)) * 100
        rows.append({
            "Area": "Data Completeness",
            "Problem": f"Missing values are present across {affected} columns.",
            "Evidence": f"{missing:,} missing cells ({pct:.2f}% of all cells).",
            "Business Impact": "Incomplete fields can reduce the reliability of segment comparisons and downstream reporting.",
            "Severity": "HIGH" if pct >= 5 else "MEDIUM"
        })

    if duplicates:
        pct = duplicates / n * 100
        rows.append({
            "Area": "Record Quality",
            "Problem": "Duplicate records are present and may affect totals or frequency-based analysis.",
            "Evidence": f"{duplicates:,} duplicate rows ({pct:.2f}% of records).",
            "Business Impact": "Repeated records can inflate counts, averages, and grouped business metrics.",
            "Severity": "HIGH" if pct >= 5 else "MEDIUM"
        })

    numeric = list(df.select_dtypes(include="number").columns)
    categorical = list(df.select_dtypes(include=["object", "category", "bool"]).columns)

    # Dominant segments: only when a categorical field has meaningful concentration.
    for col in categorical[:12]:
        series = df[col].dropna().astype(str)
        if series.empty or series.nunique() < 2 or series.nunique() > min(30, max(2, int(len(series) * 0.25))):
            continue
        shares = series.value_counts(normalize=True)
        top_value = shares.index[0]
        top_share = float(shares.iloc[0]) * 100
        if top_share >= 50:
            rows.append({
                "Area": f"{_bi_pretty(col)} Concentration",
                "Problem": f"The dataset is concentrated in the '{top_value}' segment.",
                "Evidence": f"'{top_value}' represents {top_share:.1f}% of observed records.",
                "Business Impact": "A highly concentrated segment can dominate aggregate KPIs and may hide differences in smaller groups.",
                "Severity": "MEDIUM"
            })
            break

    # Outcome/rate fields: detect only from actual values and column names.
    outcome_terms = ("status", "outcome", "result", "response", "default", "churn", "converted", "approved", "rejected", "fraud", "claim")
    for col in categorical:
        name = _bi_norm(col)
        if not any(term in name for term in outcome_terms):
            continue
        series = df[col].dropna().astype(str)
        if series.nunique() < 2 or series.nunique() > 10:
            continue
        counts = series.value_counts()
        top = counts.index[0]
        share = float(counts.iloc[0]) / len(series) * 100
        rows.append({
            "Area": f"{_bi_pretty(col)} Outcome Mix",
            "Problem": f"The observed { _bi_pretty(col).lower() } is led by '{top}'.",
            "Evidence": f"'{top}' accounts for {share:.1f}% of non-missing records ({int(counts.iloc[0]):,} of {len(series):,}).",
            "Business Impact": "The dominant outcome should be interpreted alongside the smaller outcome groups to understand balance and potential business exposure.",
            "Severity": "MEDIUM" if share >= 80 else "LOW"
        })
        break

    # Numeric dispersion and outliers.
    for col in numeric[:15]:
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if len(series) < 10 or series.nunique() < 5:
            continue
        q1, q3 = series.quantile([0.25, 0.75])
        iqr = q3 - q1
        if iqr <= 0:
            continue
        outlier_count = int(((series < q1 - 1.5 * iqr) | (series > q3 + 1.5 * iqr)).sum())
        outlier_pct = outlier_count / len(series) * 100
        if outlier_pct >= 5:
            rows.append({
                "Area": f"{_bi_pretty(col)} Variability",
                "Problem": f"The measure contains a noticeable share of values outside the interquartile range.",
                "Evidence": f"{outlier_count:,} of {len(series):,} observed values ({outlier_pct:.1f}%) fall beyond the 1.5×IQR rule.",
                "Business Impact": "Extreme values can materially influence averages and may represent important high-value or exceptional cases.",
                "Severity": "MEDIUM"
            })
            break

    # Strong numeric associations, without claiming causation.
    if len(numeric) >= 2:
        corr = df[numeric].corr(numeric_only=True).abs()
        pairs = []
        for i, a in enumerate(numeric):
            for b in numeric[i+1:]:
                value = corr.loc[a, b]
                if pd.notna(value):
                    pairs.append((float(value), a, b, float(df[[a,b]].corr().iloc[0,1])))
        if pairs:
            value, a, b, signed = max(pairs, key=lambda x: x[0])
            if value >= 0.60:
                direction = "positive" if signed > 0 else "negative"
                rows.append({
                    "Area": "Numeric Relationship",
                    "Problem": f"A strong {direction} association is visible between {_bi_pretty(a)} and {_bi_pretty(b)}.",
                    "Evidence": f"Observed Pearson correlation: {signed:.2f}.",
                    "Business Impact": "This relationship is a useful candidate for deeper analysis, segmentation, or predictive modelling; it does not establish causation.",
                    "Severity": "LOW"
                })

    # Useful numeric range insight if no richer pattern was found.
    if numeric and len(rows) < 4:
        col = numeric[0]
        series = pd.to_numeric(df[col], errors="coerce").dropna()
        if not series.empty:
            rows.append({
                "Area": f"{_bi_pretty(col)} Business Range",
                "Problem": f"The observed { _bi_pretty(col).lower() } spans a wide operating range.",
                "Evidence": f"Minimum {_bi_fmt(series.min())}; median {_bi_fmt(series.median())}; maximum {_bi_fmt(series.max())}.",
                "Business Impact": "Segmenting this measure into meaningful business bands may reveal differences that are hidden in overall averages.",
                "Severity": "LOW"
            })

    if not rows:
        rows.append({
            "Area": "Dataset Structure",
            "Problem": "No high-priority business barrier was automatically identified from the available fields.",
            "Evidence": f"The dataset contains {len(df):,} records and {len(df.columns):,} columns with the currently available structure.",
            "Business Impact": "The dashboard and statistical views should be used to investigate domain-specific patterns further.",
            "Severity": "LOW"
        })

    return pd.DataFrame(rows[:10])


=======
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572
# ==========================================================
# PAGE CONFIGURATION
# ==========================================================

st.set_page_config(
    page_title="Automated BI Platform",
    page_icon="📊",
    layout="wide"
)


# ==========================================================
# CUSTOM CSS
# ==========================================================

st.markdown(
    """
    <style>

    /* ======================================================
       REMOVE STREAMLIT DEFAULT TOP BAR / WHITE SPACE
       Keep the custom DATA ANALYZER canvas continuous.
       ====================================================== */

    header[data-testid="stHeader"],
    .stApp > header {
        background: transparent !important;
        height: 0 !important;
        min-height: 0 !important;
        border: 0 !important;
        box-shadow: none !important;
    }

    header[data-testid="stHeader"] * {
        visibility: hidden !important;
    }

    [data-testid="stToolbar"] {
        display: none !important;
    }

    [data-testid="stDecoration"] {
        display: none !important;
    }

    [data-testid="stStatusWidget"] {
        display: none !important;
    }

    div[data-testid="stAppViewContainer"] {
        background: transparent !important;
    }

    div[data-testid="stAppViewContainer"] > section.main {
        background: transparent !important;
    }

    .main .block-container {
        padding-top: 0.35rem !important;
    }

    /* ======================================================
       DATA ANALYZER — NEON ANALYTICS / AI COMMAND CENTER
       Visual direction based on the supplied reference image:
       midnight blue + electric cyan + violet + magenta + amber.
       ====================================================== */

    :root {
        --bg: #050A18;
        --bg2: #08132A;
        --panel: #0B1730;
        --panel2: #101F40;
        --panel3: #152852;
        --border: #243A67;
        --cyan: #22D3EE;
        --blue: #3B82F6;
        --violet: #8B5CF6;
        --magenta: #EC4899;
        --pink: #F472B6;
        --green: #34D399;
        --amber: #FBBF24;
        --orange: #FB923C;
        --red: #FB7185;
        --text: #F7FAFF;
        --muted: #9FB1D0;
    }

    .stApp {
        background:
            radial-gradient(circle at 12% 5%, rgba(34,211,238,.14), transparent 25%),
            radial-gradient(circle at 90% 8%, rgba(139,92,246,.17), transparent 27%),
            radial-gradient(circle at 82% 90%, rgba(236,72,153,.10), transparent 28%),
            radial-gradient(circle at 8% 88%, rgba(59,130,246,.10), transparent 25%),
            linear-gradient(135deg, #030712 0%, #071225 42%, #081A35 100%);
        color: var(--text);
    }

    .stApp::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        opacity: .20;
        background-image:
            linear-gradient(rgba(34,211,238,.06) 1px, transparent 1px),
            linear-gradient(90deg, rgba(34,211,238,.06) 1px, transparent 1px);
        background-size: 44px 44px;
        mask-image: linear-gradient(to bottom, black, transparent 85%);
        z-index: 0;
    }

    .main .block-container {
        position: relative;
        z-index: 1;
        max-width: 1500px;
        padding-top: 1.3rem;
        padding-bottom: 3rem;
    }

    /* ---------- Header ---------- */

    .main-title {
        font-size: 3.1rem;
        line-height: 1.05;
        font-weight: 900;
        letter-spacing: -.045em;
        background: linear-gradient(
            90deg,
            #FFFFFF 0%,
            #B9F7FF 28%,
            #55E7FF 52%,
            #A78BFA 78%,
            #F9A8D4 100%
        );
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        text-shadow: 0 0 30px rgba(34,211,238,.18);
    }

    .main-subtitle {
        margin-top: 7px;
        color: #82DFF5;
        font-size: 14px;
        letter-spacing: .035em;
    }

    .bi-status {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 9px 14px;
        border-radius: 999px;
        color: #B9F7FF;
        font-size: 12px;
        font-weight: 700;
        background: rgba(15,31,64,.82);
        border: 1px solid rgba(34,211,238,.32);
        box-shadow: 0 0 24px rgba(34,211,238,.08);
    }

    .hero-panel {
        position: relative;
        overflow: hidden;
        margin: 18px 0 22px;
        padding: 26px 30px;
        border-radius: 22px;
        border: 1px solid rgba(73,216,255,.36);
        background:
            radial-gradient(circle at 82% 30%, rgba(139,92,246,.26), transparent 30%),
            radial-gradient(circle at 18% 85%, rgba(34,211,238,.14), transparent 32%),
            linear-gradient(135deg, rgba(10,28,59,.96), rgba(14,30,67,.92));
        box-shadow:
            0 20px 60px rgba(0,0,0,.32),
            inset 0 1px 0 rgba(255,255,255,.05),
            0 0 40px rgba(34,211,238,.06);
    }

    .hero-panel::after {
        content: "";
        position: absolute;
        width: 260px;
        height: 260px;
        right: -80px;
        top: -120px;
        border-radius: 50%;
        background: rgba(236,72,153,.13);
        filter: blur(55px);
    }

    .hero-kicker {
        color: #63E6FF;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .16em;
        margin-bottom: 8px;
    }

    .hero-title {
        color: #F8FBFF;
        font-size: 28px;
        line-height: 1.18;
        font-weight: 850;
        margin-bottom: 9px;
    }

    .hero-copy {
        max-width: 920px;
        color: #AFC0DD;
        font-size: 14px;
        line-height: 1.7;
    }

    /* ---------- Sidebar ---------- */

    section[data-testid="stSidebar"] {
        background:
            radial-gradient(circle at 18% 10%, rgba(34,211,238,.12), transparent 28%),
            radial-gradient(circle at 90% 75%, rgba(139,92,246,.16), transparent 30%),
            linear-gradient(180deg, #050D1F 0%, #07152D 48%, #091A35 100%);
        border-right: 1px solid rgba(58,101,168,.42);
    }

    section[data-testid="stSidebar"] > div {
        background: transparent;
    }

    .bi-brand {
        padding: 8px 2px 14px;
    }

    .bi-brand-name {
        font-size: 21px;
        font-weight: 900;
        letter-spacing: .02em;
        background: linear-gradient(90deg, #F8FAFF, #61E7FF, #A78BFA);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    .bi-brand-subtitle {
        margin-top: 4px;
        color: #7FA4D5;
        font-size: 11px;
        line-height: 1.5;
    }

    section[data-testid="stSidebar"] hr {
        border-color: rgba(66,96,147,.35);
    }

    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] .stMarkdown p {
        color: #BFD0EA !important;
    }

    /* ---------- General typography ---------- */

    h1, h2, h3, h4, h5, h6 {
        color: #F4F8FF !important;
        letter-spacing: -.02em;
    }

    .section-title {
        font-size: 28px;
        font-weight: 850;
        background: linear-gradient(90deg, #FFFFFF, #60E8FF, #A78BFA);
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        margin-top: 16px;
        margin-bottom: 6px;
    }

    .stMarkdown, .stText, p, li {
        color: #B9C8E0;
    }

    .stCaption {
        color: #7891B5 !important;
    }

    /* ---------- Tabs ---------- */

    button[data-baseweb="tab"] {
        color: #8299BB !important;
        font-weight: 700 !important;
        border-radius: 10px 10px 0 0 !important;
    }

    button[data-baseweb="tab"][aria-selected="true"] {
        color: #72E9FF !important;
        background: rgba(34,211,238,.06) !important;
    }

    div[data-baseweb="tab-highlight"] {
        background: linear-gradient(
            90deg,
            #22D3EE,
            #3B82F6,
            #8B5CF6,
            #EC4899
        ) !important;
        height: 3px !important;
        box-shadow: 0 0 14px rgba(34,211,238,.45);
    }

    /* ---------- Cards / containers ---------- */

    div[data-testid="stMetric"] {
        position: relative;
        overflow: hidden;
        padding: 16px 17px;
        min-height: 118px;
        border-radius: 16px;
        border: 1px solid rgba(77,111,168,.48);
        background:
            linear-gradient(145deg, rgba(17,34,69,.96), rgba(9,22,48,.96));
        box-shadow:
            0 12px 30px rgba(0,0,0,.20),
            inset 0 1px 0 rgba(255,255,255,.045);
    }

    div[data-testid="stMetric"]::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        width: 100%;
        height: 3px;
        background: linear-gradient(
            90deg,
            #22D3EE,
            #3B82F6,
            #8B5CF6,
            #EC4899
        );
    }

    div[data-testid="stMetric"] label {
        color: #87A5CA !important;
        font-weight: 700 !important;
    }

    div[data-testid="stMetricValue"] {
        color: #F7FAFF !important;
        font-size: 1.85rem !important;
        font-weight: 850 !important;
        text-shadow: 0 0 20px rgba(34,211,238,.10);
    }

    div[data-testid="stMetricDelta"] {
        color: #5EEAD4 !important;
    }

    .business-card {
        padding: 20px;
        border-radius: 16px;
        border: 1px solid rgba(75,108,163,.45);
        background: linear-gradient(145deg, #0D1D3B, #0A1730);
        box-shadow: 0 12px 30px rgba(0,0,0,.20);
    }

    /* ---------- Buttons ---------- */

    .stButton > button,
    .stDownloadButton > button {
        border-radius: 10px !important;
        border: 1px solid rgba(62,116,193,.62) !important;
        color: #D9F8FF !important;
        background: linear-gradient(135deg, #102B55, #183C72) !important;
        box-shadow: 0 5px 18px rgba(0,0,0,.20) !important;
        font-weight: 750 !important;
        transition: all .18s ease;
    }

    .stButton > button:hover,
    .stDownloadButton > button:hover {
        border-color: #22D3EE !important;
        color: #FFFFFF !important;
        box-shadow:
            0 0 22px rgba(34,211,238,.18),
            0 8px 24px rgba(0,0,0,.24) !important;
        transform: translateY(-1px);
    }

    button[kind="primary"] {
        background: linear-gradient(
            100deg,
            #2563EB,
            #7C3AED,
            #DB2777
        ) !important;
        border-color: rgba(139,92,246,.75) !important;
    }

    /* ---------- Inputs ---------- */

    div[data-baseweb="select"] > div,
    div[data-baseweb="input"] > div,
    div[data-testid="stTextInput"] input,
    textarea {
        background: #0B1934 !important;
        color: #EAF4FF !important;
        border-color: #2C4776 !important;
    }

    div[data-baseweb="select"] span {
        color: #D7E5F7 !important;
    }

    div[data-testid="stFileUploader"] {
        padding: 4px;
        border-radius: 14px;
        background: rgba(9,25,52,.72);
        border: 1px dashed rgba(34,211,238,.55);
    }

    div[data-testid="stFileUploaderDropzone"] {
        background: linear-gradient(135deg, #0A1B37, #10264B) !important;
        border-color: rgba(67,153,225,.55) !important;
    }

    /* ---------- Expanders ---------- */

    div[data-testid="stExpander"] {
        border: 1px solid rgba(65,100,157,.45) !important;
        border-radius: 14px !important;
        background: rgba(9,24,51,.78) !important;
        overflow: hidden;
    }

    /* ---------- Alerts ---------- */

    div[data-testid="stAlert"] {
        border-radius: 13px;
        border: 1px solid rgba(67,118,181,.40);
        background: rgba(12,31,64,.80);
    }

    /* ---------- Dataframes ---------- */

    div[data-testid="stDataFrame"] {
        border: 1px solid #263F6B;
        border-radius: 14px;
        overflow: hidden;
        box-shadow: 0 10px 28px rgba(0,0,0,.20);
    }

    /* ---------- Code / links ---------- */

    code {
        color: #67E8F9 !important;
    }

    a {
        color: #67E8F9 !important;
    }

    /* ---------- Slider / checkbox / radio ---------- */

    div[data-testid="stSlider"] [role="slider"] {
        background: #22D3EE !important;
    }

    /* ---------- Dedicated dashboard ---------- */

    .neon-dashboard-title {
        font-size: 2.65rem;
        font-weight: 900;
        letter-spacing: -.04em;
        background: linear-gradient(
            90deg,
            #FFFFFF,
            #7DEBFF 35%,
            #8B5CF6 68%,
            #F472B6
        );
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
        text-shadow: 0 0 35px rgba(34,211,238,.16);
    }

    .neon-dashboard-subtitle {
        color: #8FB7DD;
        font-size: 13px;
        margin-top: 4px;
        margin-bottom: 18px;
    }

    .neon-kpi {
        position: relative;
        min-height: 125px;
        padding: 18px 19px;
        border-radius: 17px;
        overflow: hidden;
        border: 1px solid rgba(74,115,177,.48);
        background:
            radial-gradient(circle at 100% 0%, var(--glow), transparent 42%),
            linear-gradient(145deg, #102349, #09172F);
        box-shadow:
            0 14px 36px rgba(0,0,0,.25),
            inset 0 1px 0 rgba(255,255,255,.05);
    }

    .neon-kpi::before {
        content: "";
        position: absolute;
        left: 0;
        top: 0;
        height: 4px;
        width: 100%;
        background: var(--accent);
        box-shadow: 0 0 18px var(--accent);
    }

    .neon-kpi-label {
        color: #8EA8CA;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .12em;
    }

    .neon-kpi-value {
        color: #F8FBFF;
        font-size: 29px;
        line-height: 1.1;
        font-weight: 900;
        margin-top: 11px;
    }

    .neon-kpi-icon {
        position: absolute;
        right: 14px;
        top: 14px;
        width: 38px;
        height: 38px;
        border-radius: 11px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--accent);
        background: rgba(255,255,255,.055);
        border: 1px solid rgba(255,255,255,.08);
        box-shadow: 0 0 18px var(--glow);
    }

    .neon-section-card {
        padding: 15px 17px;
        border-radius: 14px;
        border: 1px solid rgba(72,107,166,.42);
        background: linear-gradient(145deg, rgba(14,31,63,.95), rgba(8,20,43,.96));
        box-shadow: 0 12px 30px rgba(0,0,0,.20);
    }

    .neon-section-label {
        color: #60E7FF;
        font-size: 11px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: .12em;
    }

    .neon-section-value {
        color: #F8FBFF;
        font-size: 17px;
        font-weight: 800;
        margin-top: 5px;
    }

    /* ---------- Scrollbars ---------- */

    ::-webkit-scrollbar {
        width: 9px;
        height: 9px;
    }

    ::-webkit-scrollbar-track {
        background: #050B18;
    }

    ::-webkit-scrollbar-thumb {
        background: #203A67;
        border-radius: 10px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #315B9A;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# SESSION STATE
# ==========================================================

if "df" not in st.session_state:
    st.session_state.df = None

if "sheets" not in st.session_state:
    st.session_state.sheets = []

if "insights" not in st.session_state:
    st.session_state.insights = pd.DataFrame()

if "recommendations" not in st.session_state:
    st.session_state.recommendations = []

if "questions" not in st.session_state:
    st.session_state.questions = []

# Used to prevent Streamlit reruns from rebuilding the dashboard
# and deleting the user's chart customizations.
if "data_key" not in st.session_state:
    st.session_state.data_key = None

if "research_result" not in st.session_state:
    st.session_state.research_result = None

if "research_sources" not in st.session_state:
    st.session_state.research_sources = []

if "basic_data_explanation" not in st.session_state:
    st.session_state.basic_data_explanation = None


# ==========================================================
# HEADER
# ==========================================================

st.markdown(
<<<<<<< HEAD
    """
    <div style="padding:4px 0 0;">
        <div class="main-title">📊 DATA ANALYZER</div>
        <div class="main-subtitle">
            Interactive Business Intelligence • AI Insights • Advanced Analytics
        </div>
    </div>
    <div class="hero-panel">
        <div class="hero-kicker">AI-powered analytics workspace</div>
        <div class="hero-title">Turn raw business data into a decision-ready command center.</div>
        <div class="hero-copy">
            Upload a CSV or Excel dataset and DATA ANALYZER automatically builds
            business-focused sheets, colourful interactive charts, statistics,
            domain research, management insights, recommendations, professional
            Ask Data questions and a compact final report.
        </div>
    </div>
    """,
=======
    '<div class="main-title">📊 Automated Business Intelligence Platform</div>',
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572
    unsafe_allow_html=True
)


# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="bi-brand">
            <div class="bi-brand-name">◈ DATA ANALYZER</div>
            <div class="bi-brand-subtitle">
                Intelligent Business Analytics Command Center
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="neon-section-card">'
        '<div class="neon-section-label">Workspace</div>'
        '<div class="neon-section-value">Upload & Configure</div>'
        '</div>',
        unsafe_allow_html=True
    )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "📁 Upload CSV / Excel",
        type=[
            "csv",
            "xlsx",
            "xls"
        ],
        help="Upload the dataset you want DATA ANALYZER to analyze."
    )

    sheet_count = st.selectbox(
        "Number of Dashboard Sheets",
        [4, 5],
        index=0
    )

    st.caption(
        "4 sheets = 20 charts\n\n"
        "5 sheets = 25 charts"
    )



# ==========================================================
# INTERACTIVE DASHBOARD PAGE
# ==========================================================


def _get_page_parameter():
    """Read the optional Streamlit page query parameter."""
    try:
        return str(st.query_params.get("page", "")).strip().lower()
    except Exception:
        try:
            params = st.experimental_get_query_params()
            value = params.get("page", [""])
            return str(value[0] if isinstance(value, list) else value).strip().lower()
        except Exception:
            return ""


def _save_dashboard_snapshot(dataframe, sheets):
    """Save the current main-app dashboard state for the dedicated page."""
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    snapshot_path = reports_dir / "dashboard_snapshot.pkl"
    with open(snapshot_path, "wb") as snapshot_file:
        pickle.dump(
            {
                "df": dataframe.copy(),
                "sheets": sheets,
            },
            snapshot_file,
        )
    return snapshot_path


def _dashboard_filter_state(sheet_index):
    """Return the filter dictionary used by the copied dashboard page."""
    if "legacy_dashboard_filters" not in st.session_state:
        st.session_state.legacy_dashboard_filters = {}
    st.session_state.legacy_dashboard_filters.setdefault(sheet_index, {})
    return st.session_state.legacy_dashboard_filters[sheet_index]


def _clear_dashboard_sheet_filter(sheet_index):
    if "legacy_dashboard_filters" in st.session_state:
        st.session_state.legacy_dashboard_filters[sheet_index] = {}


def _clear_dashboard_all_filters():
    st.session_state.legacy_dashboard_filters = {}


def _apply_dashboard_filters(dataframe, filters):
    result = dataframe.copy()
    for column, value in filters.items():
        if column not in result.columns or value in (None, "All"):
            continue
        result = result[result[column].astype(str) == str(value)]
    return result.copy()


def _dashboard_attach_selection(fig, category, dataframe):
    """Add [column, value] metadata so the old dashboard-style click filter works."""
    if not category or category not in dataframe.columns:
        return fig

    values = dataframe[category].dropna().astype(str).unique().tolist()
    if not values:
        return fig

    for trace in fig.data:
        try:
            trace_x = list(trace.x) if trace.x is not None else []
            trace_y = list(trace.y) if trace.y is not None else []

            # Most categorical charts place the category on x.
            if trace_x and len(trace_x) == len(trace_y):
                trace.customdata = [[category, str(v)] for v in trace_x]
            elif trace.labels is not None:
                labels = list(trace.labels)
                trace.customdata = [[category, str(v)] for v in labels]
            elif trace_y:
                trace.customdata = [[category, str(v)] for v in trace_y]
        except Exception:
            pass

    return fig


def _dashboard_capture_selection(event, sheet_index):
    """Read a Plotly point selection in the same way as the old dashboard."""
    if event is None:
        return False

    try:
        points = list(event.selection.points or [])
    except Exception:
        try:
            points = list(event.get("selection", {}).get("points", []))
        except Exception:
            points = []

    if not points:
        return False

    point = points[0]
    customdata = point.get("customdata")
    if not isinstance(customdata, (list, tuple)) or len(customdata) < 2:
        return False

    column = customdata[0]
    value = customdata[1]
    filters = _dashboard_filter_state(sheet_index)

    if filters.get(column) == value:
        return False

    filters[column] = value
    return True


def _dashboard_chart(fig, chart, filtered_df, sheet_index, chart_index):
    """Render one generated chart using the visual/interaction pattern of dashboard_app.py."""
    category = chart.get("category")

    fig = _dashboard_attach_selection(
        fig,
        category,
        filtered_df,
    )

    fig.update_layout(
        height=360,
        margin=dict(l=35, r=20, t=55, b=50),
        hovermode="closest",
        legend_title_text="",
    )

    event = st.plotly_chart(
        fig,
        use_container_width=True,
        key=(
            f"copied_dashboard_chart_"
            f"{sheet_index}_"
            f"{chart.get('chart_id', chart_index)}"
        ),
        on_select="rerun",
        selection_mode="points",
    )

    return _dashboard_capture_selection(event, sheet_index)


def _render_interactive_dashboard_page(df, sheets):
    """
    Dedicated dashboard page copied from the old dashboard_app.py layout.

    Important difference from the old standalone app:
    the page does NOT ask for a dataset. It uses the dataset already
    uploaded/generated by the main Automated BI application.
    """

    # If a dashboard snapshot was created by an older version in which every
    # chart used the same default blue, upgrade that snapshot to the new
    # professional palette. User-customized multi-colour dashboards are kept.
    existing_colors = [
        chart.get("color")
        for sheet in sheets or []
        for chart in sheet.get("charts", [])
        if chart.get("color")
    ]
    if existing_colors and len(set(existing_colors)) == 1:
        _apply_dashboard_palette(sheets)

    # ========================================================
    # OLD DASHBOARD STYLING / HEADER
    # ========================================================
    st.markdown(
        """
        <div class="neon-dashboard-title">◈ Analytics Command Center</div>
        <div class="neon-dashboard-subtitle">
            Interactive dashboard with AI insights, advanced analytics and
            Power BI-style sheet-level filtering.
        </div>
        <div class="hero-panel" style="margin-top:4px;">
            <div class="hero-kicker">Live business dashboard</div>
            <div class="hero-title" style="font-size:23px;">
                Explore performance, patterns and management signals.
            </div>
            <div class="hero-copy">
                Use slicers and chart selections to explore the uploaded dataset.
                Every sheet uses the same analytical source and updates its
                related charts when filters are applied.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        "[← Back to Main Analysis](http://localhost:8501/)"
    )

    # ========================================================
    # KPI CARDS — same visual idea as the old dashboard
    # ========================================================
    total_charts = sum(
        len(sheet.get("charts", []))
        for sheet in sheets
    )

    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    primary_metric = numeric_columns[0] if numeric_columns else None
    average_metric = (
        f"{df[primary_metric].mean():,.2f}"
        if primary_metric and len(df)
        else "—"
    )

    k1, k2, k3, k4 = st.columns(4)
    kpi_items = [
        (k1, "Total Records", f"{len(df):,}", "#22D3EE", "#22D3EE20", "◉"),
        (k2, "Dashboard Sheets", f"{len(sheets):,}", "#8B5CF6", "#8B5CF620", "✦"),
        (k3, "Average Metric", average_metric, "#34D399", "#34D39920", "↗"),
        (k4, "Dashboard Charts", f"{total_charts:,}", "#EC4899", "#EC489920", "◈"),
    ]
    for col, label, value, accent, glow, icon in kpi_items:
        with col:
            st.markdown(
                f'<div class="neon-kpi" style="--accent:{accent};--glow:{glow};">'
                f'<div class="neon-kpi-icon">{icon}</div>'
                f'<div class="neon-kpi-label">{label}</div>'
                f'<div class="neon-kpi-value">{value}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    st.write("")

    # ========================================================
    # GLOBAL CLEAR — copied from old dashboard
    # ========================================================
    if st.button("🧹 Clear All Sheet Filters"):
        _clear_dashboard_all_filters()
        st.rerun()

    st.divider()

    if not sheets:
        st.warning("No generated dashboard sheets are available.")
        st.markdown("[← Open Main Streamlit Application](http://localhost:8501/)")
        return

    # ========================================================
    # SHEETS — same tabs + two-column layout as old dashboard
    # ========================================================
    tabs = st.tabs([
        sheet.get("name", "Dashboard")
        for sheet in sheets
    ])

    for sheet_index, (tab, sheet) in enumerate(zip(tabs, sheets)):
        with tab:
            st.markdown(
                f'<div class="neon-section-card">'
                f'<div class="neon-section-label">ANALYTICAL SHEET</div>'
                f'<div class="neon-section-value">📁 {sheet.get("name", "Dashboard")}</div>'
                f'</div>',
                unsafe_allow_html=True
            )
            st.caption(
                sheet.get(
                    "description",
                    "Business dashboard analysis"
                )
            )

            filters = _dashboard_filter_state(sheet_index)

            c1, c2 = st.columns([5, 1])
            with c1:
                if filters:
                    st.info(
                        "🔎 Active filters: " +
                        " • ".join(
                            f"{key}: {value}"
                            for key, value in filters.items()
                        )
                    )
                else:
                    st.caption(
                        "💡 Click a category/value in a chart. "
                        "All charts on this sheet will update."
                    )
            with c2:
                if st.button(
                    "✖ Clear",
                    key=f"copy_clear_sheet_{sheet_index}",
                    disabled=not bool(filters),
                    use_container_width=True,
                ):
                    _clear_dashboard_sheet_filter(sheet_index)
                    st.rerun()

            filtered_df = _apply_dashboard_filters(df, filters)
            st.caption(
                f"Showing {len(filtered_df):,} of {len(df):,} records"
            )

            charts = sorted(
                sheet.get("charts", []),
                key=lambda chart: chart.get("position", 999)
            )

            columns = st.columns(2)

            for chart_index, chart in enumerate(charts):
                with columns[chart_index % 2]:
                    try:
                        fig = create_chart(
                            filtered_df,
                            category=chart.get("category"),
                            metric=chart.get("metric"),
                            chart_type=chart.get("chart_type", "Bar"),
                            color=chart.get("color", "#22D3EE"),
                            title=chart.get("title", "Business Chart")
                        )

                        fig = _style_neon_figure(fig, chart)

                        selection_changed = _dashboard_chart(
                            fig,
                            chart,
                            filtered_df,
                            sheet_index,
                            chart_index,
                        )

                        if selection_changed:
                            st.rerun()

                    except Exception as exc:
                        st.error(
                            f"Unable to render "
                            f"'{chart.get('title', 'Business Chart')}': {exc}"
                        )

            st.success(
                f"✅ {sheet.get('name', 'Dashboard')}: "
                f"{len(charts)} interactive charts"
            )

    st.divider()
    st.metric("TOTAL DASHBOARD CHARTS", total_charts)

    st.markdown("### 📌 Dashboard Page Link")
    st.code(
        "http://localhost:8501/?page=dashboard",
        language="text"
    )
    st.caption(
        "This dashboard is a copy of the old dashboard page layout "
        "inside the same Streamlit application. It uses the dataset "
        "already uploaded in the main application, so no second upload is required."
    )


# ==========================================================
# CHECK FOR THE DEDICATED DASHBOARD PAGE
# ==========================================================

_requested_page = _get_page_parameter()

if _requested_page == "dashboard":

    # First use the active Streamlit session.
    dashboard_df = st.session_state.get("df")
    dashboard_sheets = st.session_state.get("sheets", [])

    # If the PDF link is opened in a new browser session, recover
    # the last generated dashboard from the saved report snapshot.
    if dashboard_df is None:
        snapshot_path = Path("reports") / "dashboard_snapshot.pkl"

        if snapshot_path.exists():
            try:
                with open(snapshot_path, "rb") as snapshot_file:
                    snapshot = pickle.load(snapshot_file)

                dashboard_df = snapshot.get("df")
                dashboard_sheets = snapshot.get("sheets", [])
            except Exception as snapshot_error:
                st.error(
                    "Unable to load the saved dashboard: "
                    f"{snapshot_error}"
                )
                st.stop()

    if dashboard_df is None:
        st.warning(
            "No dashboard data is available yet. "
            "Please return to the main page and upload a dataset first."
        )
        st.markdown(
            "[← Open Main Streamlit Application](http://localhost:8501/)"
        )
        st.stop()

    _render_interactive_dashboard_page(
        dashboard_df,
        dashboard_sheets
    )

    st.stop()


# ==========================================================
# LOAD DATA
# ==========================================================

if uploaded_file:

    # Include file name, size and sheet count in the key.
    # The dashboard is regenerated only when the actual upload
    # or requested sheet count changes.
    current_data_key = (
        uploaded_file.name,
        getattr(uploaded_file, "size", None),
        sheet_count
    )

    if st.session_state.data_key != current_data_key:

        try:

            df = load_file(
                uploaded_file
            )

            df = convert_date_columns(df)

            st.session_state.df = df

            # Generate initial dashboard only once for this upload.
            st.session_state.sheets = (
                generate_sheet_templates(
                    df,
                    sheet_count
                )
            )

            # Give every chart stable metadata used by the editor
            # and by Streamlit's widget/chart keys.
            for sheet_index, sheet in enumerate(
                st.session_state.sheets
            ):
                for chart_index, chart in enumerate(
                    sheet.get("charts", [])
                ):
                    chart.setdefault(
                        "chart_id",
                        f"sheet{sheet_index}_chart{chart_index}"
                    )
                    chart.setdefault(
                        "position",
                        chart_index + 1
                    )
<<<<<<< HEAD

                    chart["color"] = DASHBOARD_PALETTE[
                        (sheet_index * 5 + chart_index) % len(DASHBOARD_PALETTE)
                    ]
=======
                    chart.setdefault(
                        "color",
                        "#2563EB"
                    )
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572

            # Generate insights
            st.session_state.insights = (
<<<<<<< HEAD
                build_business_insights(
                    df,
                    st.session_state.sheets
                )
=======
                generate_insights(df)
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572
            )

            # Automatic recommendations are generated from the uploaded data.
            # Ask Data handles user-entered questions and prediction requests.
            try:
                st.session_state.recommendations = generate_recommendations(df)
            except Exception as recommendation_error:
                st.session_state.recommendations = []
                st.warning(
                    f"Recommendation generation failed: {recommendation_error}"
                )

            # Online basic explanation of the uploaded dataset.
            try:
                st.session_state.basic_data_explanation = generate_basic_data_explanation(df)
                basic_research = st.session_state.basic_data_explanation
                st.session_state.research_result = {
                    "domain": basic_research.get("domain", "General Business Analytics"),
                    "analysis": basic_research.get("dataset_description", "No online explanation available."),
                }
                st.session_state.research_sources = basic_research.get("sources", [])
            except Exception as research_error:
                st.session_state.basic_data_explanation = {
                    "domain": _detect_business_domain(df),
                    "dataset_description": f"Online research could not be completed: {research_error}",
                    "business_uses": [],
                    "column_rows": [],
                    "online_evidence": [],
                    "sources": [],
                    "research_status": "Online research failed",
                }
                st.session_state.research_result = {
                    "domain": st.session_state.basic_data_explanation["domain"],
                    "analysis": st.session_state.basic_data_explanation["dataset_description"],
                }
                st.session_state.research_sources = []
            st.session_state.data_key = current_data_key

        except Exception as e:

            st.error(f"Unable to process file: {e}")
            st.stop()

else:

<<<<<<< HEAD
    st.markdown(
        """
        <div class="hero-panel" style="margin-top:4px;">
            <div class="hero-kicker">Workspace ready</div>
            <div class="hero-title">Your analytics command center is ready.</div>
            <div class="hero-copy">
                Start by uploading your CSV or Excel file from the sidebar.
                The platform will adapt its dashboard topics, charts, insights,
                questions and recommendations to the actual structure of your data.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("### ✦ What your workspace will generate")

    f1, f2, f3, f4 = st.columns(4)

    cards = [
        (f1, "#22D3EE", "◉", "Interactive Dashboards",
         "4–5 business sheets with 5 colourful charts per sheet."),
        (f2, "#8B5CF6", "✦", "AI Business Insights",
         "Signals, barriers, trends and management focus areas."),
        (f3, "#EC4899", "◈", "Smart Ask Data",
         "Professional questions generated from your actual data."),
        (f4, "#FB923C", "↗", "Decision Report",
         "Compact PDF report with insights and dashboard access."),
    ]

    for col, accent, icon, title, copy in cards:
        with col:
            st.markdown(
                f"""
                <div class="neon-kpi"
                     style="--accent:{accent};--glow:{accent}22;">
                    <div class="neon-kpi-icon">{icon}</div>
                    <div class="neon-kpi-label">{title}</div>
                    <div style="color:#9FB1D0;font-size:12px;line-height:1.55;margin-top:10px;">
                        {copy}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)

    st.info("👈 Upload your CSV or Excel file from the sidebar to start the analysis.")
=======
    st.info("👈 Upload your CSV or Excel file from the sidebar.")
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572
    st.stop()


# ==========================================================
# DATA INFORMATION / MAIN NAVIGATION
# ==========================================================

df = st.session_state.df
column_types = detect_column_types(df)
kpis = calculate_kpis(df)

tabs = st.tabs([
    "🏢 Overview",
    "📊 Dashboard Builder",
    "📈 Statistics",
    "🚨 Business Insights",
    "🔎 Domain Research",
    "💡 Recommendations",
    "🤖 Ask Data",
    "📄 Final Report"
])


# OVERVIEW
# ==========================================================

with tabs[0]:

    st.markdown(
        '<div class="section-title">Business Overview</div>',
        unsafe_allow_html=True
    )

    st.write(
        "This page contains only the most important "
        "information required for business understanding."
    )

    cols = st.columns(4)

    cols[0].metric(
        "Total Records",
        f"{len(df):,}"
    )

    cols[1].metric(
        "Total Columns",
        len(df.columns)
    )

    cols[2].metric(
        "Missing Values",
        f"{df.isna().sum().sum():,}"
    )

    cols[3].metric(
        "Data Quality",
        f"{get_data_quality_score(df)}%"
    )

    st.divider()

    st.subheader(
        "Business-Level Metrics"
    )

    numeric_summary = get_numeric_summary(df)

    if not numeric_summary.empty:

        st.dataframe(
            numeric_summary,
            use_container_width=True
        )

    st.subheader(
        "Data Coverage"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Numeric Columns",
        len(column_types["numeric"])
    )

    c2.metric(
        "Categorical Columns",
        len(column_types["categorical"])
    )

    c3.metric(
        "Date Columns",
        len(column_types["date"])
    )


# ==========================================================
# DASHBOARD BUILDER
# ==========================================================

with tabs[1]:

    st.markdown(
        '<div class="section-title">📊 Dashboard Builder</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Automatically generated business sheets with "
        "5 charts per sheet. Use the customizer to change "
        "the chart, metric, dimension, colour, title and position."
    )

    # ------------------------------------------------------
    # DASHBOARD CONTROLS
    # ------------------------------------------------------

    control1, control2, control3 = st.columns([2, 2, 2])

    with control1:

        if st.button(
            "🔄 Generate / Regenerate Dashboard",
            key="regenerate_dashboard",
            use_container_width=True
        ):

            st.session_state.sheets = (
                generate_sheet_templates(
                    df,
                    sheet_count
                )
            )

            for si, sheet in enumerate(
                st.session_state.sheets
            ):
                for ci, chart in enumerate(
                    sheet.get("charts", [])
                ):
                    chart["chart_id"] = (
                        f"sheet{si}_chart{ci}"
                    )
<<<<<<< HEAD

                    chart["position"] = (
                        ci + 1
                    )

                    chart["color"] = DASHBOARD_PALETTE[
                        (si * 5 + ci) % len(DASHBOARD_PALETTE)
                    ]
=======
                    chart["position"] = ci + 1
                    chart.setdefault(
                        "color",
                        "#2563EB"
                    )
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572

            st.rerun()

    with control2:

        layout_columns = st.selectbox(
            "🧩 Dashboard Layout",
            [1, 2, 3],
            index=1,
            key="dashboard_layout_columns",
            help=(
                "Choose how many chart columns are displayed "
                "in each dashboard sheet."
            )
        )

    with control3:

        total_charts = sum(
            len(sheet.get("charts", []))
            for sheet in st.session_state.sheets
        )

        st.metric(
            "📊 Dashboard Charts",
            total_charts
        )

    st.divider()

    # ------------------------------------------------------
    # SHEET TABS
    # ------------------------------------------------------

    sheet_tabs = st.tabs(
        [
            sheet["name"]
            for sheet in st.session_state.sheets
        ]
    )

    for sheet_index, (
        sheet_tab,
        sheet
    ) in enumerate(
        zip(
            sheet_tabs,
            st.session_state.sheets
        )
    ):

        with sheet_tab:

            st.subheader(
                f"📁 {sheet['name']}"
            )

            st.caption(
                sheet["description"]
            )

            charts = sheet.get("charts", [])

            # Make sure older generated sheets also have the new
            # customization metadata.
            for chart_index, chart in enumerate(charts):
                chart.setdefault(
                    "chart_id",
                    f"sheet{sheet_index}_chart{chart_index}"
                )
                chart.setdefault(
                    "position",
                    chart_index + 1
                )
<<<<<<< HEAD
=======
                chart.setdefault(
                    "color",
                    "#2563EB"
                )
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572

            st.write(
                f"Charts in this sheet: **{len(charts)}**"
            )

            st.divider()

            # ==================================================
            # EXPLICIT DASHBOARD CUSTOMIZER
            # ==================================================

            st.markdown(
                "### 🎨 Customize Dashboard"
            )

            chart_labels = [
                f"Chart {i + 1}: {chart.get('title', 'Business Chart')}"
                for i, chart in enumerate(charts)
            ]

            selected_chart_index = st.selectbox(
                "Select a chart to customize",
                range(len(charts)),
                format_func=lambda i: chart_labels[i],
                key=f"selected_chart_{sheet_index}"
            )

            selected_chart = charts[selected_chart_index]

            with st.container(border=True):

                st.markdown(
                    f"**Editing:** Chart {selected_chart_index + 1} — "
                    f"{selected_chart.get('title', 'Business Chart')}"
                )

                edit1, edit2, edit3 = st.columns(3)

                # ----------------------------------------------
                # METRIC
                # ----------------------------------------------

                with edit1:

                    numeric_options = (
                        df.select_dtypes(
                            include="number"
                        ).columns.tolist()
                    )

                    metric_options = (
                        numeric_options
                        if numeric_options
                        else ["None"]
                    )

                    current_metric = selected_chart.get(
                        "metric"
                    )

                    metric_index = (
                        metric_options.index(current_metric)
                        if current_metric in metric_options
                        else 0
                    )

                    new_metric = st.selectbox(
                        "📊 Metric",
                        metric_options,
                        index=metric_index,
                        key=f"edit_metric_{sheet_index}_{selected_chart_index}"
                    )

                    if new_metric == "None":
                        new_metric = None

                # ----------------------------------------------
                # DIMENSION
                # ----------------------------------------------

                with edit2:

                    dimension_options = ["None"] + (
                        df.select_dtypes(
                            include=[
                                "object",
                                "category",
                                "bool",
                                "datetime"
                            ]
                        ).columns.tolist()
                    )

                    current_dimension = selected_chart.get(
                        "category"
                    )

                    dimension_index = (
                        dimension_options.index(current_dimension)
                        if current_dimension in dimension_options
                        else 0
                    )

                    new_dimension = st.selectbox(
                        "🏷️ Dimension",
                        dimension_options,
                        index=dimension_index,
                        key=f"edit_dimension_{sheet_index}_{selected_chart_index}"
                    )

                    if new_dimension == "None":
                        new_dimension = None

                # ----------------------------------------------
                # CHART TYPE
                # ----------------------------------------------

                with edit3:

                    chart_types = [
                        "Bar",
                        "Line",
                        "Area",
                        "Pie",
                        "Histogram",
                        "Scatter",
                        "Box"
                    ]

                    current_type = selected_chart.get(
                        "chart_type",
                        "Bar"
                    )

                    type_index = (
                        chart_types.index(current_type)
                        if current_type in chart_types
                        else 0
                    )

                    new_chart_type = st.selectbox(
                        "📈 Chart Type",
                        chart_types,
                        index=type_index,
                        key=f"edit_type_{sheet_index}_{selected_chart_index}"
                    )

                edit4, edit5, edit6 = st.columns(3)

                # ----------------------------------------------
                # COLOUR
                # ----------------------------------------------

                with edit4:

                    new_color = st.color_picker(
                        "🎨 Chart Color",
                        selected_chart.get(
                            "color",
                            "#2563EB"
                        ),
                        key=f"edit_color_{sheet_index}_{selected_chart_index}"
                    )

                # ----------------------------------------------
                # TITLE
                # ----------------------------------------------

                with edit5:

                    new_title = st.text_input(
                        "✏️ Chart Title",
                        selected_chart.get(
                            "title",
                            "Business Chart"
                        ),
                        key=f"edit_title_{sheet_index}_{selected_chart_index}"
                    )

                # ----------------------------------------------
                # POSITION
                # ----------------------------------------------

                with edit6:

                    position_options = list(
                        range(
                            1,
                            len(charts) + 1
                        )
                    )

                    current_position = selected_chart.get(
                        "position",
                        selected_chart_index + 1
                    )

                    if current_position not in position_options:
                        current_position = selected_chart_index + 1

                    new_position = st.selectbox(
                        "↕️ Chart Position",
                        position_options,
                        index=position_options.index(
                            current_position
                        ),
                        key=f"edit_position_{sheet_index}_{selected_chart_index}",
                        help=(
                            "Position 1 appears first, position 2 "
                            "second, and so on. If another chart "
                            "already has the selected position, the "
                            "two charts will swap positions."
                        )
                    )

                # ----------------------------------------------
                # APPLY / RESET
                # ----------------------------------------------

                button1, button2 = st.columns(2)

                with button1:

                    if st.button(
                        "💾 Apply Chart Changes",
                        key=f"apply_customization_{sheet_index}_{selected_chart_index}",
                        use_container_width=True,
                        type="primary"
                    ):

                        old_position = selected_chart.get(
                            "position",
                            selected_chart_index + 1
                        )

                        # Swap positions when needed.
                        if new_position != old_position:
                            for other_index, other_chart in enumerate(charts):
                                if other_index != selected_chart_index and other_chart.get("position", other_index + 1) == new_position:
                                    other_chart["position"] = old_position
                                    break

                        selected_chart["metric"] = new_metric
                        selected_chart["category"] = new_dimension
                        selected_chart["chart_type"] = new_chart_type
                        selected_chart["color"] = new_color
                        selected_chart["title"] = new_title.strip() or "Business Chart"
                        selected_chart["position"] = new_position

                        st.success(
                            "✅ Chart customization saved."
                        )

                        st.rerun()

                with button2:

                    if st.button(
                        "🔄 Reset This Chart",
                        key=f"reset_customization_{sheet_index}_{selected_chart_index}",
                        use_container_width=True
                    ):

                        selected_chart["chart_type"] = "Bar"
<<<<<<< HEAD

                        selected_chart["color"] = "#22D3EE"

=======
                        selected_chart["color"] = "#2563EB"
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572
                        selected_chart["title"] = (
                            f"Business Chart {selected_chart_index + 1}"
                        )
                        selected_chart["position"] = (
                            selected_chart_index + 1
                        )

                        st.rerun()

            st.divider()

            # ==================================================
            # FINAL DASHBOARD PREVIEW
            # ==================================================

            st.markdown(
                "### 📊 Dashboard Preview"
            )

            ordered_charts = sorted(
                charts,
                key=lambda chart: chart.get(
                    "position",
                    999
                )
            )

            # Render the final charts in the selected dashboard
            # column layout.
            chart_columns = st.columns(
                layout_columns
            )

            for display_index, chart in enumerate(
                ordered_charts
            ):

                with chart_columns[display_index % layout_columns]:

                    fig = create_chart(
                        df,
                        category=chart.get(
                            "category"
                        ),
                        metric=chart.get(
                            "metric"
                        ),
                        chart_type=chart.get(
                            "chart_type",
                            "Bar"
                        ),
                        color=chart.get(
                            "color",
                            "#22D3EE"
                        ),
                        title=chart.get(
                            "title",
                            "Business Chart"
                        )
                    )

                    fig = _style_neon_figure(fig, chart)

                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        key=(
                            f"dashboard_chart_"
                            f"{sheet_index}_"
                            f"{chart.get('chart_id', display_index)}"
                        )
                    )

            st.success(
                f"✅ {sheet['name']} contains "
                f"{len(charts)} charts."
            )

    # ------------------------------------------------------
    # TOTAL CHART COUNT
    # ------------------------------------------------------

    st.divider()

    st.metric(
        "TOTAL DASHBOARD CHARTS",
        total_charts
    )

# ==========================================================
# STATISTICS
# ==========================================================

with tabs[2]:

    st.markdown(
        '<div class="section-title">Statistical Analysis</div>',
        unsafe_allow_html=True
    )

    st.subheader(
        "Summary Statistics"
    )

    statistics = get_summary_statistics(
        df
    )

    if not statistics.empty:

        st.dataframe(
            statistics,
            use_container_width=True
        )

    st.subheader(
        "Outlier Analysis"
    )

    outliers = detect_outliers(
        df
    )

    if not outliers.empty:

        st.dataframe(
            outliers,
            use_container_width=True
        )

    st.subheader(
        "Correlation Analysis"
    )

    correlations = calculate_correlations(
        df
    )

    if not correlations.empty:

        st.dataframe(
            correlations,
            use_container_width=True
        )


# ==========================================================
# BUSINESS INSIGHTS
# ==========================================================

with tabs[3]:

    st.markdown(
<<<<<<< HEAD
        '<div class="section-title">🚨 Business Insights</div>',
=======
        '<div class="section-title">🚨 Business Insights & Barriers</div>',
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572
        unsafe_allow_html=True
    )

    st.write(
<<<<<<< HEAD
        "This page interprets the actual dashboard and dataset "
        "evidence to identify important business patterns, barriers "
        "and areas that require further investigation."
    )
=======
        "First understand what the uploaded data represents. Then review "
        "what the actual data shows and which areas may become business barriers."
    )

    # ======================================================
    # BASIC DATA EXPLANATION FROM ONLINE RESEARCH
    # ======================================================

    basic = st.session_state.get("basic_data_explanation")

    if basic:
        st.markdown("## 📚 Basic Data Explanation")
        st.caption(basic.get("research_status", "Online research status unavailable"))

        st.markdown("### 🏢 What is this dataset?")
        st.info(basic.get("dataset_description", "No dataset explanation is available."))

        st.markdown("### 🔎 Detected Business Domain")
        st.success(basic.get("domain", "General Business Analytics"))

        st.markdown("### 🎯 What can this type of data be used for?")
        uses = basic.get("business_uses", [])
        if uses:
            for use in uses:
                st.write(f"- {use}")
        else:
            st.write("The available online research did not provide enough domain-specific information.")

        st.markdown("### 📋 Column-by-Column Explanation")
        column_rows = basic.get("column_rows", [])
        if column_rows:
            st.dataframe(pd.DataFrame(column_rows), use_container_width=True, hide_index=True)
        else:
            st.info("No column explanations were generated.")

        evidence = basic.get("online_evidence", [])
        if evidence:
            st.markdown("### 🌐 What online sources say")
            for item in evidence[:5]:
                st.write(f"- {item}")

        sources = basic.get("sources", [])
        if sources:
            st.markdown("### 📚 Online Sources Used")
            for source in sources:
                title = source.get("title", "Web Source")
                url = source.get("url", "")
                if url:
                    st.markdown(f"- [{title}]({url})")

        st.divider()

    st.markdown("## 📊 What Your Uploaded Data Shows")
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572

    insights = st.session_state.insights

    # ------------------------------------------------------
    # EXECUTIVE BUSINESS SUMMARY
    # ------------------------------------------------------

    st.markdown("### 📌 Executive Business Summary")

    if insights is None or getattr(insights, "empty", True):

        st.info(
            "No business insights were generated for this dataset."
        )

    else:

        insight_count = len(insights)
        high_count = 0
        medium_count = 0
        low_count = 0

        if "Severity" in insights.columns:
            severity_series = (
                insights["Severity"]
                .astype(str)
                .str.upper()
            )
            high_count = int((severity_series == "HIGH").sum())
            medium_count = int((severity_series == "MEDIUM").sum())
            low_count = int((severity_series == "LOW").sum())

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            st.metric("Business Findings", insight_count)

        with c2:
            st.metric("High Attention", high_count)

        with c3:
            st.metric("Medium Attention", medium_count)

        with c4:
            st.metric("Monitoring Areas", low_count)

        st.markdown(
            "The findings below are based on the available dataset "
            "evidence and the analytical outputs generated by the platform."
        )

    st.divider()

    # ------------------------------------------------------
    # KEY BUSINESS SIGNALS
    # ------------------------------------------------------

    st.markdown("### 📊 Key Business Signals")

    if insights is not None and not insights.empty:

        signal_rows = list(
            insights.head(4).iterrows()
        )

        signal_columns = st.columns(
            max(1, min(2, len(signal_rows)))
        )

        for display_index, (_, row) in enumerate(signal_rows):

            with signal_columns[display_index % len(signal_columns)]:

                area = str(
                    row.get("Area", "Business Area")
                )

                problem = str(
                    row.get("Problem", "Important business pattern identified.")
                )

                evidence = str(
                    row.get("Evidence", "Evidence available in the analysis.")
                )

                severity = str(
                    row.get("Severity", "INFO")
                ).upper()

                icon = {
                    "HIGH": "🔴",
                    "MEDIUM": "🟠",
                    "LOW": "🔵"
                }.get(severity, "🔵")

                st.markdown(
                    f"""
                    <div class="business-card">
                        <h4>{icon} {area}</h4>
                        <p><b>What the data shows:</b><br>{problem}</p>
                        <p><b>Evidence:</b><br>{evidence}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

    else:

        st.info("No key business signals are available yet.")

    st.divider()

    # ------------------------------------------------------
    # BUSINESS PROBLEMS / BARRIERS
    # ------------------------------------------------------

    st.markdown("### 🚨 Business Problems / Barriers")

    if insights is not None and not insights.empty:

        for _, row in insights.iterrows():

            area = str(
                row.get("Area", "Business Area")
            )

            problem = str(
                row.get("Problem", "Business pattern identified.")
            )

            impact = str(
                row.get("Business Impact", "Further business investigation may be required.")
            )

            evidence = str(
                row.get("Evidence", "Evidence available in the dataset analysis.")
            )

            severity = str(
                row.get("Severity", "INFO")
            ).upper()

            if severity == "HIGH":
                st.error(
                    f"🔴 {area}\n\n"
                    f"**Problem:** {problem}\n\n"
                    f"**Why it matters:** {impact}\n\n"
                    f"**Evidence:** {evidence}"
                )

            elif severity == "MEDIUM":
                st.warning(
                    f"🟠 {area}\n\n"
                    f"**Problem:** {problem}\n\n"
                    f"**Why it matters:** {impact}\n\n"
                    f"**Evidence:** {evidence}"
                )

            else:
                st.info(
                    f"🔵 {area}\n\n"
                    f"**Problem / Observation:** {problem}\n\n"
                    f"**Why it matters:** {impact}\n\n"
                    f"**Evidence:** {evidence}"
                )

    else:

        st.info(
            "The application could not identify a business barrier "
            "from the available evidence."
        )

    st.divider()

    # ------------------------------------------------------
    # IMPORTANT TRENDS
    # ------------------------------------------------------

    st.markdown("### 📈 Important Trends / Patterns")

    if insights is not None and not insights.empty:

        for _, row in insights.head(6).iterrows():

            area = str(
                row.get("Area", "Business Area")
            )

            problem = str(
                row.get("Problem", "Pattern identified from the dataset.")
            )

            st.markdown(
                f"**{area} →** {problem}"
            )

    else:

        st.info("No trend-level observations are available.")

    st.divider()

    # ------------------------------------------------------
    # DATA QUALITY / ATTENTION AREAS
    # ------------------------------------------------------

    st.markdown("### ⚠️ Areas Requiring Attention")

    missing_total = int(
        df.isna().sum().sum()
    )

    duplicate_total = int(
        df.duplicated().sum()
    )

    attention_items = []

    if missing_total > 0:
        attention_items.append(
            f"🟠 Missing data requires review across "
            f"{int((df.isna().sum() > 0).sum())} columns."
        )
    else:
        attention_items.append(
            "🟢 No missing values were detected in the uploaded dataset."
        )

    if duplicate_total > 0:
        attention_items.append(
            f"🟠 {duplicate_total:,} duplicate rows require review."
        )
    else:
        attention_items.append(
            "🟢 No duplicate rows were detected."
        )

    for item in attention_items:
        st.markdown(f"- {item}")

    # ------------------------------------------------------
    # OVERALL BUSINESS INTERPRETATION
    # ------------------------------------------------------

    st.divider()

    st.markdown("### 📌 Overall Business Interpretation")

    if insights is not None and not insights.empty:

        areas = []
        for _, row in insights.head(5).iterrows():
            area = str(row.get("Area", ""))
            if area and area not in areas:
                areas.append(area)

        focus_text = ", ".join(areas)

        st.success(
            "The dataset contains business patterns that can be "
            "translated into specific areas for investigation. "
            f"The main areas identified by the current analysis are: "
            f"{focus_text}. Review the dashboard charts and statistical "
            "results before making operational decisions."
        )

    else:

        st.info(
            "No overall business interpretation is available yet."
        )


# ==========================================================
# DOMAIN RESEARCH
# ==========================================================

with tabs[4]:

    st.markdown(
        '<div class="section-title">🔎 Domain Research</div>',
        unsafe_allow_html=True
    )

    research = st.session_state.research_result
<<<<<<< HEAD
    detailed_research = st.session_state.get(
        "basic_data_explanation",
        None
    )
=======
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572

    if not research:

        st.info(
            "Upload a dataset to start domain research."
        )

    else:

        domain = research.get(
            "domain",
            "General Data Analysis"
        )

<<<<<<< HEAD
        # --------------------------------------------------
        # DETECTED DOMAIN
        # --------------------------------------------------

        st.markdown(
            f"""
            <div style="background:#E8F8EE;padding:20px 24px;"
                 "border-radius:12px;color:#087F3F;font-size:18px;">
                🔎 <b>Detected dataset domain:</b> {domain}
            </div>
            """,
            unsafe_allow_html=True
=======
        st.success(
            f"🔎 Detected dataset domain: {domain}"
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572
        )

        st.divider()

<<<<<<< HEAD
        # --------------------------------------------------
        # RESEARCH BASED ANALYSIS
        # --------------------------------------------------

        st.markdown("### 🌐 Research-Based Analysis")

=======
        st.markdown("### 🌐 Research-Based Analysis")

>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572
        st.write(
            research.get(
                "analysis",
                "No research result available."
            )
        )

<<<<<<< HEAD
        # --------------------------------------------------
        # WHAT IS THIS DATASET?
        # --------------------------------------------------

        st.markdown("### 🏢 What is this dataset?")

        dataset_description = (
            detailed_research.get(
                "dataset_description"
            )
            if detailed_research
            else research.get(
                "analysis",
                "No dataset explanation available."
            )
        )

        st.info(dataset_description)

        # --------------------------------------------------
        # DETECTED BUSINESS DOMAIN
        # --------------------------------------------------

        st.markdown("### 🔎 Detected Business Domain")

        st.success(domain)

        # --------------------------------------------------
        # DATASET PROFILE
        # --------------------------------------------------

        st.markdown("### 📊 Dataset Profile")

        numeric_count = len(
            df.select_dtypes(include="number").columns
        )

        categorical_count = len(
            df.select_dtypes(
                include=["object", "category", "bool"]
            ).columns
        )

        date_count = len(
            df.select_dtypes(
                include=["datetime"]
            ).columns
        )

        missing_count = int(
            df.isna().sum().sum()
        )

        duplicate_count = int(
            df.duplicated().sum()
        )

        profile_cols = st.columns(6)

        profile_values = [
            ("Records", f"{len(df):,}"),
            ("Columns", f"{len(df.columns):,}"),
            ("Numeric", f"{numeric_count:,}"),
            ("Categorical", f"{categorical_count:,}"),
            ("Missing", f"{missing_count:,}"),
            ("Duplicates", f"{duplicate_count:,}"),
        ]

        for column, (label, value) in zip(
            profile_cols,
            profile_values
        ):
            with column:
                st.metric(label, value)

        # --------------------------------------------------
        # WHAT CAN THIS DATA BE USED FOR?
        # --------------------------------------------------

        st.markdown("### 🎯 What can this type of data be used for?")

        business_uses = (
            detailed_research.get(
                "business_uses",
                []
            )
            if detailed_research
            else []
        )

        if not business_uses:
            business_uses = [
                "Business performance monitoring",
                "Trend and group comparison",
                "Data quality monitoring",
                "Identification of important business patterns",
                "Decision support and further investigation",
            ]

        for use_case in business_uses:
            st.markdown(
                f"- {use_case}"
            )

        # --------------------------------------------------
        # IMPORTANT VARIABLES
        # --------------------------------------------------

        st.markdown("### ⭐ Important Variables")

        numeric_columns = [
            str(c)
            for c in df.select_dtypes(
                include="number"
            ).columns
        ]

        categorical_columns = [
            str(c)
            for c in df.select_dtypes(
                include=["object", "category", "bool"]
            ).columns
        ]

        variable_cols = st.columns(2)

        with variable_cols[0]:
            st.markdown("**📌 KPI / Measure Candidates**")
            if numeric_columns:
                for col in numeric_columns[:10]:
                    st.markdown(f"- `{col}`")
            else:
                st.write("No numeric measures detected.")

        with variable_cols[1]:
            st.markdown("**📌 Dimension / Segmentation Candidates**")
            if categorical_columns:
                for col in categorical_columns[:10]:
                    st.markdown(f"- `{col}`")
            else:
                st.write("No categorical dimensions detected.")

        # --------------------------------------------------
        # COLUMN-BY-COLUMN EXPLANATION
        # --------------------------------------------------

        st.markdown("### 📋 Column-by-Column Explanation")

        column_rows = (
            detailed_research.get(
                "column_rows",
                []
            )
            if detailed_research
            else []
        )

        if column_rows:

            column_df = pd.DataFrame(
                column_rows
            )

            st.dataframe(
                column_df,
                use_container_width=True,
                hide_index=True
            )

        else:

            fallback_rows = []

            for column in df.columns:

                series = df[column]
                dtype = str(series.dtype)

                fallback_rows.append(
                    {
                        "Column": column,
                        "Data Type": dtype,
                        "Meaning / Explanation": (
                            "Numeric field that can be summarized and compared."
                            if pd.api.types.is_numeric_dtype(series)
                            else
                            "Categorical/text field that can be grouped and compared."
                        ),
                        "Missing Values": int(series.isna().sum()),
                        "Unique Values": int(series.nunique(dropna=True)),
                    }
                )

            st.dataframe(
                pd.DataFrame(fallback_rows),
                use_container_width=True,
                hide_index=True
            )

        # --------------------------------------------------
        # POTENTIAL RELATIONSHIPS
        # --------------------------------------------------

        st.markdown("### 🔗 Potential Variable Relationships")

        if len(numeric_columns) >= 2:

            st.info(
                "Potential relationships to investigate: "
                f"`{numeric_columns[0]}` ↔ `{numeric_columns[1]}`"
                + (
                    f", `{numeric_columns[0]}` ↔ `{numeric_columns[2]}`."
                    if len(numeric_columns) >= 3
                    else "."
                )
                + " These are analytical candidates, not proof of causation."
            )

        elif numeric_columns and categorical_columns:

            st.info(
                f"Compare `{numeric_columns[0]}` across "
                f"`{categorical_columns[0]}` to investigate group-level patterns."
            )

        else:

            st.info(
                "The current dataset does not contain enough structured "
                "fields to suggest a variable relationship automatically."
            )

        # --------------------------------------------------
        # BUSINESS QUESTIONS
        # --------------------------------------------------

        st.markdown("### 💬 Business Questions This Dataset Can Answer")

        generated_questions = generate_data_questions(
            df
        )

        for index, question in enumerate(
            generated_questions[:10],
            start=1
        ):
            st.markdown(
                f"**{index}.** {question}"
            )

        # --------------------------------------------------
        # DATA QUALITY OBSERVATIONS
        # --------------------------------------------------

        st.markdown("### 🧹 Data Quality Observations")

        if missing_count == 0:
            st.success(
                "No missing values were detected in the uploaded dataset."
            )
        else:
            st.warning(
                f"{missing_count:,} missing values were detected. "
                "Columns containing missing data should be reviewed before modeling or reporting."
            )

        if duplicate_count == 0:
            st.success(
                "No duplicate rows were detected."
            )
        else:
            st.warning(
                f"{duplicate_count:,} duplicate rows were detected. "
                "Review whether they represent valid repeated observations or duplicate records."
            )

        # --------------------------------------------------
        # RESEARCH SOURCES
        # --------------------------------------------------

=======
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572
        sources = st.session_state.research_sources

        if sources:

<<<<<<< HEAD
            st.markdown("### 📚 Research Sources")
=======
            st.divider()

            st.markdown("### 📚 Web Sources")
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572

            for source in sources:

                title = source.get(
                    "title",
                    "Web Source"
                )

                url = source.get(
                    "url",
                    ""
                )

                snippet = source.get(
                    "snippet",
                    ""
                )

                if url:

                    st.markdown(
                        f"**{title}**"
                    )
<<<<<<< HEAD
                    if snippet:
                        st.caption(snippet)
                    st.markdown(
                        f"[Open source →]({url})"
                    )
                    st.divider()

        else:

            st.caption(
                "No external research sources were returned. "
                "The displayed explanations are based on the uploaded dataset structure."
            )

        st.caption(
            "Field meanings that cannot be verified from an authoritative "
            "source are presented as analytical interpretations rather than "
            "confirmed data-dictionary definitions."
        )
=======
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572


# RECOMMENDATIONS
# ==========================================================

with tabs[5]:

    st.markdown(
        '<div class="section-title">💡 Recommendations</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Recommendations are generated from the actual uploaded "
        "dataset. Each business problem is evaluated using the "
        "available data before a recommendation is produced."
    )

    st.divider()

    # ======================================================
    # GENERATE RECOMMENDATIONS
    # ======================================================

    recommendations = st.session_state.get(
        "recommendations",
        []
    )

    if not recommendations:

        st.info(
            "No recommendation areas were identified "
            "from the uploaded dataset."
        )

    else:

        # ==================================================
        # ANALYSIS SUMMARY
        # ==================================================

        st.markdown(
            "## 📊 Analysis Summary"
        )

        st.write(
            f"{len(recommendations)} data-driven analysis "
            "areas were identified from the uploaded dataset."
        )

        st.divider()

        # ==================================================
        # EACH RECOMMENDATION
        # ==================================================

        for index, rec in enumerate(
            recommendations,
            start=1
        ):

            business_area = rec.get(
                "Business Area",
                "Business Analysis"
            )

            status = rec.get(
                "Status",
                "🟡 Needs Investigation"
            )

            # ----------------------------------------------
            # STATUS
            # ----------------------------------------------

            if "🔴" in status:

                status_title = (
                    "🔴 Problem Detected"
                )

            elif "🟢" in status:

                status_title = (
                    "🟢 No Evidence Detected"
                )

            else:

                status_title = (
                    "🟡 Needs Investigation"
                )

            # ==================================================
            # TITLE
            # ==================================================

            st.markdown(
                f"## 📌 {index}. {business_area}"
            )

            st.markdown(
                f"### {status_title}"
            )

            # ==================================================
            # DATA EVIDENCE
            # ==================================================

            st.markdown(
                "### 📊 Data Evidence"
            )

            evidence = rec.get(
                "Evidence",
                "No specific evidence was generated."
            )

            st.info(
                evidence
            )

            # ==================================================
            # DETAILED ANALYSIS
            # ==================================================

            st.markdown(
                "### 🔎 Detailed Analysis"
            )

            detailed_analysis = rec.get(
                "Detailed Analysis",
                ""
            )

            if detailed_analysis:

                st.write(
                    detailed_analysis
                )

            # ==================================================
            # FACTOR ANALYSIS
            # ==================================================

            factor_analysis = rec.get(
                "Factor Analysis",
                ""
            )

            if factor_analysis:

                st.markdown(
                    "### 📈 Factor / Group Analysis"
                )

                st.code(
                    factor_analysis,
                    language="text"
                )

            # ==================================================
            # BUSINESS PROBLEM
            # ==================================================

            st.markdown(
                "### ⚠️ Business Problem"
            )

            business_problem = rec.get(
                "Business Impact",
                ""
            )

            if business_problem:

                st.write(
                    business_problem
                )

            # ==================================================
            # CORRECTIVE MEASURES
            # ==================================================

            st.markdown(
                "### 🛠️ Corrective Measures"
            )

            corrective_measures = rec.get(
                "Corrective Measures",
                []
            )

            if corrective_measures:

                for number, action in enumerate(
                    corrective_measures,
                    start=1
                ):

                    st.write(
                        f"**{number}.** {action}"
                    )

            else:

                st.write(
                    "No immediate corrective action is "
                    "required based on the available data."
                )

            # ==================================================
            # HOW TO IMPROVE CURRENT WORKING
            # ==================================================

            st.markdown(
                "### 🔧 How to Improve Current Working"
            )

            improvement = rec.get(
                "How to Improve Working",
                ""
            )

            if improvement:

                st.write(
                    improvement
                )

            # ==================================================
            # WORKFLOW
            # ==================================================

            workflow = rec.get(
                "Workflow",
                ""
            )

            if workflow:

                st.markdown(
                    "### 🔄 Recommended Review Process"
                )

                st.code(
                    workflow,
                    language="text"
                )

            # ==================================================
            # DEVELOPMENT OPPORTUNITY
            # ==================================================

            st.markdown(
                "### 🚀 Development Opportunity"
            )

            development = rec.get(
                "Development Opportunity",
                ""
            )

            if development:

                st.success(
                    development
                )

            # ==================================================
            # EXPECTED OUTCOME
            # ==================================================

            st.markdown(
                "### 🎯 Expected Outcome"
            )

            expected = rec.get(
                "Expected Outcome",
                ""
            )

            if expected:

                st.write(
                    expected
                )

            # ==================================================
            # ADDITIONAL DATA REQUIRED
            # ==================================================

            additional_data = rec.get(
                "Additional Data Required",
                []
            )

            if additional_data:

                st.markdown(
                    "### 📥 Additional Data Required"
                )

                for item in additional_data:

                    st.write(
                        f"- {item}"
                    )

            # ==================================================
            # LIMITATION
            # ==================================================

            st.markdown(
                "### ⚠️ Limitation"
            )

            limitation = rec.get(
                "Limitation",
                (
                    "The dataset shows patterns and "
                    "associations. It does not automatically "
                    "prove causation."
                )
            )

            st.warning(
                limitation
            )

            st.divider()

<<<<<<< HEAD

# ==========================================================
# REAL DATA-DRIVEN ASK DATA ENGINE
# ==========================================================

def _find_column_ci(df, candidates):

    lookup = {
        str(c).strip().lower(): c
        for c in df.columns
    }

    for c in candidates:

        key = str(c).strip().lower()

        if key in lookup:
            return lookup[key]

    return None


def _binary_positive_mask(series):

    values = (
        series
        .astype(str)
        .str.strip()
        .str.lower()
    )

    positive = {
        "yes",
        "y",
        "1",
        "true",
        "left",
        "leaver",
        "attrited",
        "churned",
        "fraud",
        "default",
        "converted",
        "purchase",
        "purchased"
    }

    return values.isin(
        positive
    )


def _answer_user_request(df, request, target_dimension=None):
    """Answer professional natural-language questions directly from the uploaded dataframe."""
    if df is None or df.empty:
        return {
            "mode": "analysis",
            "title": "No Data",
            "answer": "Please upload a dataset before asking a question.",
            "evidence": "No dataframe is currently available.",
            "table": None,
            "note": "Upload a CSV or Excel dataset and ask a business question."
        }

    q_original = str(request or "").strip()
    if not q_original:
        return None

    q = q_original.lower().strip()

    def normalize(value):
        return re.sub(r"[^a-z0-9]+", " ", str(value).lower()).strip()

    normalized_q = normalize(q)
    all_columns = list(df.columns)
    numeric_columns = df.select_dtypes(include="number").columns.tolist()
    categorical_columns = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    def find_column(columns, aliases):
        normalized_columns = {c: normalize(c) for c in columns}
        # Exact/contained matches first.
        for alias in aliases:
            a = normalize(alias)
            for col, col_norm in normalized_columns.items():
                if col_norm == a or (a and a in col_norm) or (col_norm and col_norm in a):
                    return col
        # Word-set match.
        for alias in aliases:
            a_words = set(normalize(alias).split())
            if not a_words:
                continue
            for col, col_norm in normalized_columns.items():
                if a_words.issubset(set(col_norm.split())):
                    return col
        return None

    def mentioned_column(columns):
        # Prefer exact column-name phrases and longer names.
        ordered = sorted(columns, key=lambda c: len(normalize(c)), reverse=True)
        for col in ordered:
            n = normalize(col)
            if n and n in normalized_q:
                return col
        return None

    # ------------------------------------------------------
    # Detect outcome/target columns before generic numeric logic.
    # This is the important fix for questions such as:
    # "Which department has the highest attrition?"
    # ------------------------------------------------------
    attrition_col = find_column(all_columns, [
        "Attrition", "Employee Attrition", "Turnover", "Employee Turnover", "Left"
    ])
    churn_col = find_column(all_columns, ["Churn", "Customer Churn", "Churn Status"])
    outcome_col = find_column(all_columns, [
        "Default", "Fraud", "Converted", "Conversion", "Response", "Purchased",
        "Purchase", "Returned", "Defect", "Stockout", "Late", "Outcome", "Status"
    ])

    target_col = target_dimension if target_dimension in all_columns else None
    if target_col is None:
        if attrition_col and any(x in normalized_q for x in ["attrition", "turnover", "left employee"]):
            target_col = attrition_col
        elif churn_col and "churn" in normalized_q:
            target_col = churn_col
        elif outcome_col and any(x in normalized_q for x in [
            "default", "fraud", "converted", "conversion", "response", "purchased",
            "purchase", "returned", "defect", "stockout", "late", "outcome", "status"
        ]):
            target_col = outcome_col

    def positive_mask(series):
        """Return a boolean mask for the positive outcome in common binary targets."""
        s = series.copy()
        if pd.api.types.is_numeric_dtype(s):
            numeric = pd.to_numeric(s, errors="coerce")
            # Common binary encodings: 1 = positive, 0 = negative.
            if numeric.notna().any() and set(numeric.dropna().unique()).issubset({0, 1}):
                return numeric.eq(1).fillna(False)

        positive_words = {
            "yes", "y", "true", "1", "left", "attrited", "attrition", "churned", "churn",
            "default", "fraud", "converted", "conversion", "purchased", "purchase",
            "returned", "return", "defect", "defective", "late", "stockout", "positive"
        }
        values = s.astype(str).str.strip().str.lower()
        normalized_values = values.map(normalize)
        return normalized_values.apply(
            lambda v: v in positive_words or any(w in v for w in positive_words if len(w) > 3)
        ).fillna(False)

    # Detect the dimension explicitly named in the question.
    dimension = None
    if target_col is not None:
        dimension_candidates = [c for c in all_columns if c != target_col]
    else:
        dimension_candidates = all_columns

    dimension = mentioned_column(dimension_candidates)

    if dimension is None:
        dimension_aliases = [
            "department", "job role", "jobrole", "business travel", "overtime", "gender",
            "marital status", "education", "education field", "job level", "job satisfaction",
            "work life balance", "worklifebalance", "environment satisfaction", "relationship satisfaction",
            "performance rating", "region", "city", "state", "country", "category", "product",
            "customer", "segment", "channel", "campaign", "branch", "contract", "payment method", "service"
        ]
        dimension = find_column(all_columns, dimension_aliases)
        if dimension == target_col:
            dimension = None

    # If the question says "department", "job role", etc., do not let a
    # numeric metric be mistaken for the requested dimension.
    if dimension is None and target_dimension in all_columns and target_dimension != target_col:
        dimension = target_dimension

    metric = mentioned_column(numeric_columns)
    if metric is None:
        metric = find_column(numeric_columns, [
            "Sales", "Revenue", "Profit", "Amount", "Income", "Monthly Income", "Salary",
            "Hourly Rate", "Daily Rate", "Monthly Rate", "Price", "Quantity", "Demand",
            "Cost", "Spend", "Years At Company", "YearsAtCompany", "Age", "Job Level",
            "Performance Rating", "Job Satisfaction", "Work Life Balance"
        ])

    asks_highest = any(x in normalized_q for x in ["highest", "maximum", "max", "most", "largest", "greatest", "top"])
    asks_lowest = any(x in normalized_q for x in ["lowest", "minimum", "min", "least", "smallest"])
    asks_average = any(x in normalized_q for x in ["average", "mean", "avg"])
    asks_total = any(x in normalized_q for x in ["total", "sum"])
    asks_count = any(x in normalized_q for x in [
        "how many", "number of", "count", "most employees", "most records",
        "highest number of records", "least records", "most common"
    ])
    asks_rate = any(x in normalized_q for x in ["rate", "percentage", "percent", "%", "ratio", "proportion"])

    # ======================================================
    # 1. TARGET / OUTCOME QUESTIONS FIRST
    # ======================================================
    if target_col is not None:
        valid_target = df[target_col].dropna()

        if asks_rate and len(valid_target) > 0:
            positive = int(positive_mask(valid_target).sum())
            rate = positive / len(valid_target) * 100
            return {
                "mode": "analysis",
                "title": f"Overall {target_col} Rate",
                "answer": f"The overall {target_col.lower()} rate is {rate:.1f}%.",
                "evidence": f"{positive:,} of {len(valid_target):,} non-missing {target_col} records represent the positive outcome.",
                "table": pd.DataFrame({
                    "Metric": [f"{target_col} Rate"],
                    "Positive Records": [positive],
                    "Records": [len(valid_target)],
                    "Rate (%)": [rate]
                }),
                "note": "Calculated directly from the uploaded dataset."
            }

        if dimension is not None:
            temp = df[[dimension, target_col]].copy()
            temp[dimension] = temp[dimension].fillna("Missing").astype(str).str.strip()
            temp["_Positive"] = positive_mask(temp[target_col]).astype(int)
            temp["_ValidTarget"] = temp[target_col].notna().astype(int)

            grouped = temp.groupby(dimension, dropna=False).agg(
                Records=("_ValidTarget", "sum"),
                Positive=("_Positive", "sum")
            ).reset_index()
            grouped = grouped[grouped["Records"] > 0].copy()
            grouped["Rate (%)"] = grouped["Positive"] / grouped["Records"] * 100

            if not grouped.empty and (asks_highest or asks_lowest or asks_rate or target_col.lower() in normalized_q):
                ascending = asks_lowest and not asks_highest
                result_table = grouped.sort_values("Rate (%)", ascending=ascending).reset_index(drop=True)
                selected = result_table.iloc[0]
                direction = "lowest" if ascending else "highest"
                label = selected[dimension]
                return {
                    "mode": "analysis",
                    "title": f"{target_col} Rate by {dimension}",
                    "answer": (
                        f"'{label}' has the {direction} observed {target_col.lower()} rate "
                        f"among {dimension} groups: {selected['Rate (%)']:.1f}%."
                    ),
                    "evidence": (
                        f"{int(selected['Positive']):,} of {int(selected['Records']):,} records in "
                        f"'{label}' are marked as the positive {target_col.lower()} outcome."
                    ),
                    "table": result_table.head(20),
                    "note": "This is an observed group-level rate calculated from the uploaded data; it does not establish causation."
                }

    # ======================================================
    # 2. CATEGORY / GROUP RECORD COUNTS
    # ======================================================
    if dimension is not None and asks_count:
        values = df[dimension].fillna("Missing").astype(str).str.strip()
        counts = values.value_counts(dropna=False).rename("Records").reset_index()
        counts.columns = [str(dimension), "Records"]
        ascending = asks_lowest and not asks_highest
        table = counts.sort_values("Records", ascending=ascending).reset_index(drop=True)
        row = table.iloc[0]
        direction = "lowest" if ascending else "highest"
        return {
            "mode": "analysis",
            "title": f"{direction.title()} Record Count — {dimension}",
            "answer": f"'{row[str(dimension)]}' has the {direction} number of records in {dimension}: {int(row['Records']):,}.",
            "evidence": f"Records were grouped by {dimension} and counted directly from the uploaded data.",
            "table": table.head(20),
            "note": "This is a descriptive record-count comparison."
        }

    # ======================================================
    # 3. CATEGORY + NUMERIC METRIC
    # ======================================================
    if dimension is not None and metric is not None:
        work = df[[dimension, metric]].copy()
        work[metric] = pd.to_numeric(work[metric], errors="coerce")
        work = work.dropna(subset=[metric])

        if not work.empty:
            grouped = work.groupby(dimension, dropna=False)[metric].agg(
                Records="count", Average="mean", Total="sum"
            ).reset_index()

            if asks_highest and asks_average:
                table = grouped.sort_values("Average", ascending=False).reset_index(drop=True)
                row = table.iloc[0]
                return {
                    "mode": "analysis",
                    "title": f"Highest Average {metric} by {dimension}",
                    "answer": f"'{row[dimension]}' has the highest average {metric}: {row['Average']:,.2f}.",
                    "evidence": f"The average {metric} was calculated for every {dimension} group.",
                    "table": table.head(20),
                    "note": "Observed group-level averages calculated directly from the uploaded data."
                }

            if asks_lowest and asks_average:
                table = grouped.sort_values("Average", ascending=True).reset_index(drop=True)
                row = table.iloc[0]
                return {
                    "mode": "analysis",
                    "title": f"Lowest Average {metric} by {dimension}",
                    "answer": f"'{row[dimension]}' has the lowest average {metric}: {row['Average']:,.2f}.",
                    "evidence": f"The average {metric} was calculated for every {dimension} group.",
                    "table": table.head(20),
                    "note": "Observed group-level averages calculated directly from the uploaded data."
                }

            if asks_highest and asks_total:
                table = grouped.sort_values("Total", ascending=False).reset_index(drop=True)
                row = table.iloc[0]
                return {
                    "mode": "analysis",
                    "title": f"Highest Total {metric} by {dimension}",
                    "answer": f"'{row[dimension]}' has the highest total {metric}: {row['Total']:,.2f}.",
                    "evidence": f"Total {metric} was calculated for every {dimension} group.",
                    "table": table.head(20),
                    "note": "Calculated directly from the uploaded data."
                }

            if asks_lowest and asks_total:
                table = grouped.sort_values("Total", ascending=True).reset_index(drop=True)
                row = table.iloc[0]
                return {
                    "mode": "analysis",
                    "title": f"Lowest Total {metric} by {dimension}",
                    "answer": f"'{row[dimension]}' has the lowest total {metric}: {row['Total']:,.2f}.",
                    "evidence": f"Total {metric} was calculated for every {dimension} group.",
                    "table": table.head(20),
                    "note": "Calculated directly from the uploaded data."
                }

            if asks_average:
                table = grouped.sort_values("Average", ascending=False).reset_index(drop=True)
                return {
                    "mode": "analysis",
                    "title": f"Average {metric} by {dimension}",
                    "answer": f"The overall average {metric} is {work[metric].mean():,.2f}. The table shows how it varies across {dimension}.",
                    "evidence": f"{len(work):,} non-missing {metric} values were used.",
                    "table": table.head(20),
                    "note": "Calculated directly from the uploaded dataframe."
                }

            if asks_total:
                table = grouped.sort_values("Total", ascending=False).reset_index(drop=True)
                return {
                    "mode": "analysis",
                    "title": f"Total {metric} by {dimension}",
                    "answer": f"The total {metric} is {work[metric].sum():,.2f}. The table shows the contribution of each {dimension} group.",
                    "evidence": f"{len(work):,} non-missing {metric} values were included.",
                    "table": table.head(20),
                    "note": "Calculated directly from the uploaded dataframe."
                }

    # ======================================================
    # 4. OVERALL NUMERIC QUESTIONS
    # ======================================================
    if metric is not None:
        values = pd.to_numeric(df[metric], errors="coerce").dropna()
        if len(values) > 0:
            if asks_average:
                value = float(values.mean())
                return {
                    "mode": "analysis",
                    "title": f"Average {metric}",
                    "answer": f"The average {metric} is {value:,.2f}.",
                    "evidence": f"Calculated using {len(values):,} non-missing {metric} values.",
                    "table": pd.DataFrame({"Metric": [metric], "Average": [value], "Records Used": [len(values)]}),
                    "note": "Calculated directly from the uploaded dataframe."
                }
            if asks_highest:
                value = float(values.max())
                return {
                    "mode": "analysis",
                    "title": f"Highest {metric}",
                    "answer": f"The highest {metric} is {value:,.2f}.",
                    "evidence": f"Calculated from {len(values):,} non-missing values.",
                    "table": pd.DataFrame({"Metric": [metric], "Highest Value": [value]}),
                    "note": "Calculated directly from the uploaded dataframe."
                }
            if asks_lowest:
                value = float(values.min())
                return {
                    "mode": "analysis",
                    "title": f"Lowest {metric}",
                    "answer": f"The lowest {metric} is {value:,.2f}.",
                    "evidence": f"Calculated from {len(values):,} non-missing values.",
                    "table": pd.DataFrame({"Metric": [metric], "Lowest Value": [value]}),
                    "note": "Calculated directly from the uploaded dataframe."
                }

    # ======================================================
    # 5. BASIC DATASET QUESTIONS
    # ======================================================
    if any(x in normalized_q for x in ["how many records", "number of records", "how many rows", "number of rows", "record count"]):
        return {
            "mode": "analysis",
            "title": "Dataset Records",
            "answer": f"The dataset contains {len(df):,} records.",
            "evidence": f"The uploaded dataframe contains {len(df):,} rows.",
            "table": None,
            "note": "Calculated directly from the uploaded data."
        }

    if any(x in normalized_q for x in ["how many columns", "number of columns", "columns available", "number of fields"]):
        return {
            "mode": "analysis",
            "title": "Dataset Columns",
            "answer": f"The dataset contains {len(df.columns):,} columns.",
            "evidence": "Available columns: " + ", ".join(map(str, df.columns)),
            "table": pd.DataFrame({"Column": list(df.columns), "Data Type": [str(x) for x in df.dtypes]}),
            "note": "Column count and types are calculated from the uploaded data."
        }

    if any(x in normalized_q for x in ["missing", "null values", "nulls", "incomplete data"]):
        missing = df.isna().sum().sort_values(ascending=False)
        missing = missing[missing > 0]
        if missing.empty:
            return {
                "mode": "analysis", "title": "Missing Values",
                "answer": "No missing values were detected.",
                "evidence": f"All {len(df.columns):,} columns contain complete values.",
                "table": None, "note": "Calculated from the uploaded dataframe."
            }
        table = missing.rename("Missing Values").reset_index()
        table.columns = ["Column", "Missing Values"]
        return {
            "mode": "analysis", "title": "Missing Values",
            "answer": f"{int(missing.sum()):,} missing cells were found across {len(missing):,} columns.",
            "evidence": "The table identifies columns containing missing values.",
            "table": table, "note": "Calculated directly from the uploaded data."
        }

    if "duplicate" in normalized_q:
        duplicate_count = int(df.duplicated().sum())
        return {
            "mode": "analysis", "title": "Duplicate Records",
            "answer": "No exact duplicate rows were detected." if duplicate_count == 0 else f"{duplicate_count:,} exact duplicate rows were detected.",
            "evidence": f"The dataframe contains {duplicate_count:,} exact duplicate rows.",
            "table": None, "note": "This checks complete-row duplicates."
        }

    # ------------------------------------------------------
    # Fallback: expose real available dimensions and metrics.
    # ------------------------------------------------------
    available_dimensions = [str(c) for c in categorical_columns[:12]]
    available_metrics = [str(c) for c in numeric_columns[:12]]
    return {
        "mode": "analysis",
        "title": "Question Needs Clarification",
        "answer": "I could not identify a reliable calculation for that question from the uploaded data.",
        "evidence": (
            "Available business dimensions: " + (", ".join(available_dimensions) if available_dimensions else "None") +
            ". Available numeric metrics: " + (", ".join(available_metrics) if available_metrics else "None") + "."
        ),
        "table": None,
        "note": (
            "Try a question such as: 'Which department has the highest attrition?', "
            "'Which job role has the highest average monthly income?', "
            "'What is the average monthly income by department?', or "
            "'Which department has the most employees?'"
        )
    }


def _render_real_user_analysis(st, df):

    st.markdown("## 🎯 User Analysis / Prediction Request")
    st.write(
        "Ask a question about the uploaded dataset. "
        "The answer below is calculated from the current data."
    )

    if "real_user_request" not in st.session_state:
        st.session_state["real_user_request"] = ""

    if "real_user_result" not in st.session_state:
        st.session_state["real_user_result"] = None

    # ======================================================
    # DATASET-SPECIFIC DEFAULT QUESTIONS
    # ======================================================
    suggested_questions = generate_data_questions(df)

    st.markdown("### 💡 Suggested Questions")
    st.caption(
        "Choose a question below, or type your own question. "
        "The questions are generated from this dataset."
    )

    def choose_question(question):
        st.session_state["real_user_request"] = question
        try:
            st.session_state["real_user_result"] = _answer_user_request(df, question, None)
        except Exception as exc:
            st.session_state["real_user_result"] = {
                "mode": "analysis",
                "title": "Question processing error",
                "answer": "I could not calculate the answer for this question.",
                "evidence": str(exc),
                "table": None,
                "note": "Please try the question again or type it manually."
            }

    for i in range(0, len(suggested_questions), 2):
        cols = st.columns(2)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(suggested_questions):
                continue
            with col:
                st.button(
                    suggested_questions[idx],
                    key=f"suggested_question_{idx}",
                    use_container_width=True,
                    on_click=choose_question,
                    args=(suggested_questions[idx],)
                )

    # ======================================================
    # USER QUESTION
    # ======================================================
    st.markdown("### ✍️ Ask Your Own Question")

    request = st.text_input(
        "What would you like to analyse or predict?",
        key="real_user_request",
        placeholder="e.g. Which department has highest attrition?"
    )

    target_options = ["Auto-detect"] + [str(c) for c in df.columns]

    selected_target = st.selectbox(
        "🎯 Target / Dimension (Optional)",
        target_options,
        key="real_user_target"
    )

    target = None if selected_target == "Auto-detect" else selected_target

    if st.button(
        "🔎 Analyse My Request",
        type="primary",
        use_container_width=True
    ):
        if not request.strip():
            st.warning("Please select a suggested question or type your own question.")
        else:
            try:
                st.session_state["real_user_result"] = _answer_user_request(df, request, target)
            except Exception as exc:
                st.session_state["real_user_result"] = {
                    "mode": "analysis",
                    "title": "Question processing error",
                    "answer": "I could not calculate the answer for this question.",
                    "evidence": str(exc),
                    "table": None,
                    "note": "Please check the question and column name, then try again."
                }

    result = st.session_state.get("real_user_result")

    if result:
        st.markdown("---")
        st.markdown("## 🎯 User-Requested Analysis")
        st.write(f"**Your request:** {request}")
        st.write(f"**Detected Mode:** 📊 {result['mode'].title()}")

        if target:
            st.write(f"**Target / Dimension:** `{target}`")

        st.markdown("### ✅ Exact Answer")
        st.success(result["answer"])

        st.markdown("### 📊 Evidence from Your Data")
        st.info(result["evidence"])

        if result.get("table") is not None:
            st.dataframe(
                result["table"],
                use_container_width=True,
                hide_index=True
            )

        st.caption(result["note"])

    # ======================================================
    # COMMON DATASET PROBLEMS — calculated from df
    # ======================================================
    st.markdown("## 📊 Common Dataset Problems")
    st.caption(
        "These statuses are calculated from the uploaded dataset. Nothing is hard-coded."
    )

    cards = []

    missing_cells = int(df.isna().sum().sum())
    missing_cols = int((df.isna().sum() > 0).sum())

    if missing_cells == 0:
        cards.append((
            "🟢",
            "No Problem Detected — Missing / Incomplete Data",
            f"0 missing cells across {len(df.columns)} columns."
        ))
    else:
        cards.append((
            "🔴",
            "Problem Detected — Missing / Incomplete Data",
            f"{missing_cells:,} missing cells across {missing_cols:,} columns."
        ))

    duplicates = int(df.duplicated().sum())

    if duplicates == 0:
        cards.append((
            "🟢",
            "No Problem Detected — Duplicate Records",
            "0 exact duplicate rows detected."
        ))
    else:
        cards.append((
            "🔴",
            "Problem Detected — Duplicate Records",
            f"{duplicates:,} exact duplicate rows detected."
        ))

    for icon, title, description in cards:
        st.markdown(f"### {icon} {title}")
        st.write(description)

=======
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572
# ==========================================================
# ASK DATA
# ==========================================================

with tabs[6]:

    st.markdown(
        '<div class="section-title">🤖 AI Data Analyst</div>',
        unsafe_allow_html=True
    )

    st.write(
        "Use this section for your own questions, analysis requests "
        "and prediction requests. Automatic business recommendations "
        "are kept separate in the Recommendations tab."
    )

<<<<<<< HEAD
    if (
        df is not None
        and not df.empty
    ):

        _render_real_user_analysis(
            st,
            df
        )

    else:

        st.info(
            "Upload a dataset first to use the AI Data Analyst."
        )
=======
    render_user_demand_section(
        st=st,
        df=df
    )
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572


# ==========================================================
# FINAL REPORT
# ==========================================================

with tabs[7]:

    st.markdown(
        '<div class="section-title">📄 Final Business Report</div>',
        unsafe_allow_html=True
    )

    total_charts = sum(
        len(sheet["charts"])
        for sheet in st.session_state.sheets
    )

    st.metric(
        "Charts Included",
        total_charts
    )

    st.write(
        "The final report will contain:"
    )

    st.write(
        """
        ✅ Business Overview

        ✅ All Dashboard Sheets

        ✅ All Dashboard Charts

        ✅ Statistical Analysis

        ✅ Domain / Web Research

        ✅ Business Problems / Barriers

        ✅ Detailed Recommendations

        ✅ Development Opportunities

        ✅ User-requested AI Analysis

        ✅ Interactive Streamlit Dashboard
        """
    )

    if st.button(
        "📄 Generate Final PDF Report"
    ):

        reports_dir = Path(
            "reports"
        )

        # Important:
        # Avoid the previous WinError 183
        # when reports already exists.

        if reports_dir.exists():

            if not reports_dir.is_dir():

                st.error(
                    "A file named 'reports' exists. "
                    "Rename/delete that file and create "
                    "a folder named 'reports'."
                )

                st.stop()

        else:

            reports_dir.mkdir(
                parents=True,
                exist_ok=True
            )

        pdf_path = (
            reports_dir /
            "automated_bi_report.pdf"
        )

        try:

            # ==================================================
<<<<<<< HEAD
            # 1. SAVE CURRENT DASHBOARD STATE
            # ==================================================

            _save_dashboard_snapshot(
                df,
                st.session_state.sheets
            )

            # ==================================================
            # 2. LINK TO THE DEDICATED DASHBOARD PAGE
            # ==================================================

            # This is a page inside THIS Streamlit application.
            # It does not start dashboard_app.py and does not use
            # port 8502.
            dashboard_url = "http://localhost:8501/?page=dashboard"

            # ==================================================
            # 3. BUILD THE COMPLETE ASK DATA QUESTION SET
            # ==================================================
            # Ask Data displays the questions generated from the current
            # dataset.  The PDF must contain that SAME complete list, and
            # every question that can be calculated should carry its
            # calculated answer into the report.
            pdf_questions = []
            seen_pdf_questions = set()

            for question in generate_data_questions(df):
                question_text = re.sub(
                    r"\s+",
                    " ",
                    str(question)
                ).strip()

                if not question_text:
                    continue

                question_key = question_text.lower()
                if question_key in seen_pdf_questions:
                    continue
                seen_pdf_questions.add(question_key)

                try:
                    answer_result = _answer_user_request(
                        df,
                        question_text,
                        None
                    )
                except Exception as question_error:
                    answer_result = {
                        "mode": "analysis",
                        "title": "Answer could not be calculated",
                        "answer": "The question could not be reliably calculated from the uploaded data.",
                        "evidence": str(question_error),
                        "table": None,
                        "note": "The question is retained in the PDF because it is part of the Ask Data question set."
                    }

                pdf_questions.append({
                    "question": question_text,
                    "answer": (
                        answer_result.get("answer", "")
                        if isinstance(answer_result, dict)
                        else str(answer_result or "")
                    ),
                    "evidence": (
                        answer_result.get("evidence", "")
                        if isinstance(answer_result, dict)
                        else ""
                    ),
                    "note": (
                        answer_result.get("note", "")
                        if isinstance(answer_result, dict)
                        else ""
                    ),
                    "answerable": bool(
                        isinstance(answer_result, dict)
                        and answer_result.get("answer")
                        and "could not identify a reliable calculation"
                        not in str(answer_result.get("answer", "")).lower()
                    ),
                })

            # Keep the same complete question/answer set available to the
            # report generator without changing the Ask Data page layout.
            st.session_state.pdf_questions = pdf_questions

            # ==================================================
            # 4. GENERATE PDF WITH AUTOMATIC DASHBOARD URL
            # ==================================================
=======
            # SAVE DASHBOARD SNAPSHOT FOR dashboard_app.py
            # ==================================================
            snapshot_path = reports_dir / "dashboard_snapshot.pkl"

            with open(snapshot_path, "wb") as snapshot_file:
                pickle.dump(
                    {
                        "df": df,
                        "sheets": st.session_state.sheets,
                    },
                    snapshot_file,
                )

            # ==================================================
            # INTERACTIVE DASHBOARD URL
            # ==================================================
            dashboard_url = "http://localhost:8502"
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572

            generate_pdf(

                str(pdf_path),

                df,

                kpis,

                st.session_state.sheets,

                st.session_state.insights,

                st.session_state.recommendations,

                pdf_questions,

<<<<<<< HEAD
                st.session_state.get(
                    "research_result"
                ),

                st.session_state.get(
                    "research_sources",
                    []
                ),

                st.session_state.get(
                    "basic_data_explanation"
                ),

                st.session_state.get(
                    "real_user_result"
                ),

                dashboard_url
=======
                dashboard_url=dashboard_url
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572
            )

            # ==================================================
            # 4. DOWNLOAD PDF
            # ==================================================

            with open(
                pdf_path,
                "rb"
            ) as file:

                st.download_button(

                    "⬇️ Download Final PDF",

                    data=file,

                    file_name=(
                        "automated_bi_report.pdf"
                    ),

                    mime="application/pdf"
                )

            st.success(
                "Final report generated successfully. "
                "The dashboard URL was detected automatically."
            )

            # ==================================================
            # 5. SHOW AUTOMATIC DASHBOARD LINK
            # ==================================================

            st.markdown(
                "### 📊 Interactive Dashboard"
            )

            st.markdown(
                f"[🔗 OPEN INTERACTIVE DASHBOARD PAGE]({dashboard_url})"
            )

            st.caption(
                "This opens the dedicated dashboard page inside the "
                "same Streamlit application. The same page link is "
                "embedded as a clickable link inside the generated PDF."
            )

            st.markdown(
                "### 📊 Interactive Dashboard"
            )

            st.markdown(
                "[🔗 OPEN STREAMLIT DASHBOARD](http://localhost:8502)"
            )

            st.caption(
                "Start dashboard_app.py on port 8502 before opening this link."
            )

        except Exception as e:

            st.error(
                f"Report generation error: {e}"
            )


# ==========================================================
# FOOTER
# ==========================================================

st.divider()

<<<<<<< HEAD
st.markdown(
    """
    <div style="
        text-align:center;
        padding:16px 8px;
        color:#617A9F;
        font-size:11px;
        letter-spacing:.04em;
    ">
        <span style="color:#22D3EE;">◆</span>
        DATA ANALYZER
        <span style="color:#8B5CF6;">•</span>
        Automated Business Intelligence
        <span style="color:#EC4899;">•</span>
        Data → Dashboard → Insights → Decisions
    </div>
    """,
    unsafe_allow_html=True
=======
st.caption(
    "Automated Business Intelligence Platform | "
    "Data → Dashboard → Statistics → Insights → "
    "Recommendations → AI Analysis → Report"
>>>>>>> 3f38de2a889e96d62248baa9c073a7ba99a56572
)
