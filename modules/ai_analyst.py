# ============================================================
# modules/ai_analyst.py
# Automated BI - AI Business Analyst / Ask Data Engine
# ============================================================

import os
import re
import json
import math
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


# ------------------------------------------------------------
# OPTIONAL .ENV SUPPORT
# ------------------------------------------------------------
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


# ============================================================
# BASIC HELPERS
# ============================================================

def _normalise(value: Any) -> str:
    """Convert text into a simple searchable format."""
    if value is None:
        return ""

    text = str(value).strip().lower()

    text = re.sub(r"[_\-\/]+", " ", text)
    text = re.sub(r"[^a-z0-9\s%]", "", text)
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def _clean_column_name(value: Any) -> str:
    return str(value).strip()


def _numeric_columns(df: pd.DataFrame) -> List[str]:
    cols = []

    for col in df.columns:
        try:
            if pd.api.types.is_numeric_dtype(df[col]):
                cols.append(str(col))
        except Exception:
            pass

    return cols


def _categorical_columns(df: pd.DataFrame) -> List[str]:
    cols = []

    for col in df.columns:
        try:
            if (
                pd.api.types.is_object_dtype(df[col])
                or pd.api.types.is_categorical_dtype(df[col])
                or pd.api.types.is_bool_dtype(df[col])
            ):
                cols.append(str(col))
        except Exception:
            pass

    return cols


def _date_columns(df: pd.DataFrame) -> List[str]:
    result = []

    for col in df.columns:

        try:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                result.append(str(col))
                continue

            if pd.api.types.is_object_dtype(df[col]):

                sample = df[col].dropna().astype(str).head(100)

                if len(sample) == 0:
                    continue

                parsed = pd.to_datetime(
                    sample,
                    errors="coerce"
                )

                if parsed.notna().mean() >= 0.75:
                    result.append(str(col))

        except Exception:
            continue

    return result


def _safe_numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def _safe_percentage(numerator: float, denominator: float) -> float:
    if denominator is None or denominator == 0:
        return 0.0

    return (numerator / denominator) * 100


def _format_number(value: Any) -> str:

    if value is None:
        return ""

    try:

        value = float(value)

        if math.isnan(value):
            return ""

        if abs(value) >= 1_000_000_000:
            return f"{value / 1_000_000_000:.2f}B"

        if abs(value) >= 1_000_000:
            return f"{value / 1_000_000:.2f}M"

        if abs(value) >= 1_000:
            return f"{value:,.0f}"

        if value.is_integer():
            return f"{int(value):,}"

        return f"{value:,.2f}"

    except Exception:
        return str(value)


def _format_percent(value: Any) -> str:

    try:
        return f"{float(value):.1f}%"
    except Exception:
        return str(value)


def _contains(text: str, words: List[str]) -> bool:

    text = _normalise(text)

    return any(
        _normalise(word) in text
        for word in words
    )


# ============================================================
# COLUMN MATCHING
# ============================================================

def _column_aliases(column: str) -> List[str]:

    original = str(column)

    normal = _normalise(original)

    aliases = {
        normal,
        normal.replace(" ", ""),
    }

    # Common abbreviations / aliases
    replacements = {
        "revenue": ["sales", "income", "turnover"],
        "sales": ["revenue"],
        "amount": ["value", "loan amount", "purchase amount"],
        "income": ["salary", "annual income"],
        "salary": ["income"],
        "customer": ["client"],
        "employee": ["staff", "worker"],
        "department": ["dept"],
        "product": ["item"],
        "category": ["segment", "type"],
        "region": ["area", "zone", "location"],
        "gender": ["sex"],
        "age": ["customer age", "employee age"],
    }

    for key, vals in replacements.items():

        if key in normal:

            for v in vals:
                aliases.add(v)

    return list(aliases)


def _find_column(
    df: pd.DataFrame,
    question: str,
    preferred_keywords: Optional[List[str]] = None
) -> Optional[str]:

    if df is None or df.empty:
        return None

    q = _normalise(question)

    candidates = []

    for col in df.columns:

        col_text = _normalise(col)

        score = 0

        if col_text in q:
            score += 100

        if col_text.replace(" ", "") in q.replace(" ", ""):
            score += 80

        for alias in _column_aliases(str(col)):

            if alias and alias in q:
                score += 30

        if preferred_keywords:

            for keyword in preferred_keywords:

                if _normalise(keyword) in col_text:
                    score += 20

        if score > 0:
            candidates.append((score, str(col)))

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: (-x[0], x[1])
    )

    return candidates[0][1]


# ============================================================
# BUSINESS METRIC DETECTION
# ============================================================

METRIC_KEYWORDS = {

    "sales": [
        "sales",
        "sale",
        "revenue",
        "turnover",
        "selling"
    ],

    "profit": [
        "profit",
        "margin",
        "profitability"
    ],

    "cost": [
        "cost",
        "expense",
        "spending",
        "expenditure"
    ],

    "amount": [
        "amount",
        "value",
        "price",
        "loan amount",
        "purchase value"
    ],

    "income": [
        "income",
        "salary",
        "earnings",
        "pay"
    ],

    "quantity": [
        "quantity",
        "units",
        "volume"
    ],

    "age": [
        "age"
    ],

    "score": [
        "score",
        "rating",
        "satisfaction"
    ],

    "tenure": [
        "tenure",
        "years at company",
        "experience"
    ],

    "demand": [
        "demand",
        "orders",
        "order volume"
    ],

    "spend": [
        "spend",
        "spending",
        "expenditure"
    ]
}


def _detect_metric(
    df: pd.DataFrame,
    question: str
) -> Optional[str]:

    q = _normalise(question)

    numeric = _numeric_columns(df)

    # First use exact column mentions
    exact = _find_column(df, question)

    if exact in numeric:
        return exact

    # Keyword-based detection
    for metric, keywords in METRIC_KEYWORDS.items():

        if any(
            _normalise(k) in q
            for k in keywords
        ):

            for col in numeric:

                c = _normalise(col)

                if metric in c:
                    return col

                for keyword in keywords:
                    if _normalise(keyword) in c:
                        return col

    # Do not blindly select a numeric column for every question.
    return None


# ============================================================
# DIMENSION DETECTION
# ============================================================

DIMENSION_KEYWORDS = [
    "department",
    "dept",
    "category",
    "product",
    "region",
    "location",
    "city",
    "state",
    "gender",
    "sex",
    "segment",
    "customer",
    "employee",
    "education",
    "qualification",
    "marital",
    "occupation",
    "job",
    "role",
    "status",
    "type",
    "channel",
    "campaign",
    "country",
    "branch",
    "store",
    "class",
    "grade",
    "income group",
    "age group"
]


def _detect_dimension(
    df: pd.DataFrame,
    question: str
) -> Optional[str]:

    # First check explicit column reference
    explicit = _find_column(df, question)

    if explicit:
        return explicit

    q = _normalise(question)

    categorical = _categorical_columns(df)

    candidates = []

    for col in categorical:

        c = _normalise(col)

        score = 0

        if c in q:
            score += 100

        if c.replace(" ", "") in q.replace(" ", ""):
            score += 80

        for keyword in DIMENSION_KEYWORDS:

            if _normalise(keyword) in c:
                if _normalise(keyword) in q:
                    score += 40

        if score:
            candidates.append((score, col))

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: (-x[0], x[1])
    )

    return candidates[0][1]


# ============================================================
# DOMAIN DETECTION
# ============================================================

def _detect_domain(df: pd.DataFrame) -> str:

    text = " ".join(
        _normalise(c)
        for c in df.columns
    )

    if any(
        word in text
        for word in [
            "loan",
            "mortgage",
            "credit",
            "income",
            "securities account",
            "personal loan"
        ]
    ):
        return "Finance / Customer Lending"

    if any(
        word in text
        for word in [
            "employee",
            "attrition",
            "department",
            "job satisfaction",
            "years at company",
            "monthly income"
        ]
    ):
        return "Human Resources"

    if any(
        word in text
        for word in [
            "sales",
            "revenue",
            "profit",
            "product",
            "quantity",
            "discount"
        ]
    ):
        return "Sales / Retail"

    if any(
        word in text
        for word in [
            "campaign",
            "marketing",
            "click",
            "conversion",
            "lead",
            "impression"
        ]
    ):
        return "Marketing"

    if any(
        word in text
        for word in [
            "patient",
            "diagnosis",
            "hospital",
            "medical",
            "treatment"
        ]
    ):
        return "Healthcare"

    if any(
        word in text
        for word in [
            "student",
            "marks",
            "grade",
            "education",
            "attendance"
        ]
    ):
        return "Education"

    if any(
        word in text
        for word in [
            "machine",
            "defect",
            "production",
            "manufacturing",
            "maintenance"
        ]
    ):
        return "Manufacturing"

    if any(
        word in text
        for word in [
            "churn",
            "telecom",
            "contract",
            "internet service"
        ]
    ):
        return "Telecom"

    return "General Business Analytics"


# ============================================================
# TARGET / OUTCOME DETECTION
# ============================================================

TARGET_KEYWORDS = [

    "loan",
    "churn",
    "attrition",
    "default",
    "converted",
    "conversion",
    "response",
    "purchase",
    "target",
    "status",
    "outcome",
    "approved",
    "approval",
    "ownership",
    "account",
    "yes",
    "no"
]


def _detect_target(
    df: pd.DataFrame,
    question: str
) -> Optional[str]:

    q = _normalise(question)

    categorical = _categorical_columns(df)

    candidates = []

    for col in categorical:

        c = _normalise(col)

        score = 0

        if c in q:
            score += 100

        for keyword in TARGET_KEYWORDS:

            k = _normalise(keyword)

            if k in c:
                score += 30

            if k in q and k in c:
                score += 50

        # Binary columns are useful outcome candidates
        try:

            nunique = df[col].dropna().nunique()

            if nunique == 2:
                score += 10

        except Exception:
            pass

        if score > 0:
            candidates.append(
                (score, col)
            )

    if not candidates:
        return None

    candidates.sort(
        key=lambda x: (-x[0], x[1])
    )

    return candidates[0][1]


# ============================================================
# BOOLEAN / BINARY DETECTION
# ============================================================

def _binary_columns(
    df: pd.DataFrame
) -> List[str]:

    result = []

    for col in df.columns:

        try:

            values = (
                df[col]
                .dropna()
                .astype(str)
                .str.strip()
                .str.lower()
                .unique()
            )

            if len(values) == 2:
                result.append(str(col))

        except Exception:
            pass

    return result


def _find_positive_value(
    series: pd.Series
) -> Optional[Any]:

    values = series.dropna().unique()

    if len(values) == 0:
        return None

    positive_words = [
        "yes",
        "y",
        "true",
        "1",
        "approved",
        "converted",
        "churn",
        "attrition",
        "accepted",
        "positive"
    ]

    for value in values:

        text = _normalise(value)

        if text in positive_words:
            return value

    # If 0/1, choose 1
    try:

        numeric = pd.to_numeric(
            pd.Series(values),
            errors="coerce"
        )

        if set(numeric.dropna().tolist()) == {0, 1}:
            return values[
                list(numeric).index(1)
            ]

    except Exception:
        pass

    # Otherwise use second category as positive
    if len(values) == 2:
        return values[1]

    return None


# ============================================================
# DATA QUALITY
# ============================================================

def _data_quality_summary(
    df: pd.DataFrame
) -> Dict[str, Any]:

    rows = len(df)

    columns = len(df.columns)

    missing = int(
        df.isna().sum().sum()
    )

    duplicate_rows = int(
        df.duplicated().sum()
    )

    total_cells = rows * columns

    missing_percentage = (
        missing / total_cells * 100
        if total_cells
        else 0
    )

    return {
        "rows": rows,
        "columns": columns,
        "missing_values": missing,
        "missing_percentage": round(
            missing_percentage,
            2
        ),
        "duplicate_rows": duplicate_rows
    }


# ============================================================
# GROUP ANALYSIS
# ============================================================

def _group_summary(
    df: pd.DataFrame,
    dimension: str,
    metric: Optional[str] = None,
    top_n: int = 10
) -> pd.DataFrame:

    if dimension not in df.columns:
        return pd.DataFrame()

    work = df.copy()

    if metric and metric in work.columns:

        work[metric] = _safe_numeric(
            work[metric]
        )

        result = (
            work
            .groupby(dimension, dropna=False)[metric]
            .agg(
                count="count",
                total="sum",
                average="mean",
                median="median"
            )
            .reset_index()
        )

        result = result.sort_values(
            "total",
            ascending=False
        )

    else:

        result = (
            work[dimension]
            .value_counts(dropna=False)
            .reset_index()
        )

        result.columns = [
            dimension,
            "count"
        ]

    return result.head(top_n)


# ============================================================
# TARGET RATE ANALYSIS
# ============================================================

def _target_rate_by_dimension(
    df: pd.DataFrame,
    target: str,
    dimension: str,
    positive_value: Optional[Any] = None
) -> pd.DataFrame:

    if (
        target not in df.columns
        or dimension not in df.columns
    ):
        return pd.DataFrame()

    work = df[
        [target, dimension]
    ].copy()

    work = work.dropna(
        subset=[target]
    )

    if positive_value is None:
        positive_value = _find_positive_value(
            work[target]
        )

    if positive_value is None:
        return pd.DataFrame()

    work["_positive"] = (
        work[target].astype(str).str.lower()
        ==
        str(positive_value).lower()
    )

    result = (
        work
        .groupby(dimension, dropna=False)
        .agg(
            customers=(target, "size"),
            positive_count=("_positive", "sum")
        )
        .reset_index()
    )

    result["rate"] = (
        result["positive_count"]
        /
        result["customers"]
        * 100
    )

    result = result.sort_values(
        "rate",
        ascending=False
    )

    return result


# ============================================================
# QUESTION-SPECIFIC EVIDENCE GENERATOR
# ============================================================

def _build_question_evidence(
    df: pd.DataFrame,
    question: str,
    target: Optional[str] = None
) -> Dict[str, Any]:

    evidence = {
        "question": question,
        "domain": _detect_domain(df),
        "tables": [],
        "observations": [],
        "relevant_columns": []
    }

    numeric = _numeric_columns(df)

    categorical = _categorical_columns(df)

    date_cols = _date_columns(df)

    metric = _detect_metric(
        df,
        question
    )

    dimension = _detect_dimension(
        df,
        question
    )

    detected_target = target or _detect_target(
        df,
        question
    )

    if metric:
        evidence["relevant_columns"].append(
            metric
        )

    if dimension:
        evidence["relevant_columns"].append(
            dimension
        )

    if detected_target:
        evidence["relevant_columns"].append(
            detected_target
        )

    # --------------------------------------------------------
    # 1. Target / outcome analysis
    # --------------------------------------------------------

    target_words = [
        "associated",
        "association",
        "participation",
        "ownership",
        "conversion",
        "churn",
        "attrition",
        "response",
        "approval",
        "approved",
        "outcome",
        "characteristics",
        "factors"
    ]

    if (
        detected_target
        and any(
            word in _normalise(question)
            for word in target_words
        )
    ):

        target_values = (
            df[detected_target]
            .dropna()
            .value_counts()
        )

        evidence["tables"].append({
            "type": "target_distribution",
            "target": detected_target,
            "values": target_values
                .head(10)
                .to_dict()
        })

        # Analyze categorical columns
        for col in categorical:

            if col == detected_target:
                continue

            try:

                nunique = df[col].nunique()

                if nunique < 2 or nunique > 30:
                    continue

                rate_df = _target_rate_by_dimension(
                    df,
                    detected_target,
                    col
                )

                if not rate_df.empty:

                    evidence["tables"].append({
                        "type": "target_rate_by_dimension",
                        "target": detected_target,
                        "dimension": col,
                        "data": rate_df
                            .head(10)
                            .to_dict("records")
                    })

            except Exception:
                continue

    # --------------------------------------------------------
    # 2. Explicit metric + dimension
    # --------------------------------------------------------

    if metric and dimension:

        try:

            grouped = _group_summary(
                df,
                dimension,
                metric,
                top_n=15
            )

            if not grouped.empty:

                evidence["tables"].append({
                    "type": "group_metric",
                    "dimension": dimension,
                    "metric": metric,
                    "data": grouped
                        .to_dict("records")
                })

        except Exception:
            pass

    # --------------------------------------------------------
    # 3. Generic categorical distributions
    # --------------------------------------------------------

    q = _normalise(question)

    for col in categorical:

        col_normal = _normalise(col)

        if (
            col_normal in q
            or any(
                word in q
                for word in DIMENSION_KEYWORDS
                if word in col_normal
            )
        ):

            try:

                counts = (
                    df[col]
                    .value_counts(
                        dropna=False
                    )
                    .head(15)
                )

                evidence["tables"].append({
                    "type": "category_distribution",
                    "column": col,
                    "data": counts.to_dict()
                })

            except Exception:
                pass

    # --------------------------------------------------------
    # 4. Numeric correlations
    # --------------------------------------------------------

    if len(numeric) >= 2:

        try:

            corr = df[numeric].corr(
                numeric_only=True
            )

            pairs = []

            for i, c1 in enumerate(
                numeric
            ):

                for c2 in numeric[
                    i + 1:
                ]:

                    try:

                        value = corr.loc[
                            c1,
                            c2
                        ]

                        if pd.notna(value):

                            pairs.append({
                                "column_1": c1,
                                "column_2": c2,
                                "correlation": round(
                                    float(value),
                                    3
                                )
                            })

                    except Exception:
                        pass

            pairs.sort(
                key=lambda x:
                abs(x["correlation"]),
                reverse=True
            )

            evidence["tables"].append({
                "type": "correlations",
                "data": pairs[:10]
            })

        except Exception:
            pass

    # --------------------------------------------------------
    # 5. Date trend
    # --------------------------------------------------------

    if date_cols:

        date_col = date_cols[0]

        try:

            date_series = pd.to_datetime(
                df[date_col],
                errors="coerce"
            )

            temp = df.copy()

            temp["_date"] = date_series

            temp = temp.dropna(
                subset=["_date"]
            )

            if metric and metric in temp.columns:

                temp["_metric"] = _safe_numeric(
                    temp[metric]
                )

                trend = (
                    temp
                    .groupby(
                        temp["_date"].dt.to_period("M")
                    )["_metric"]
                    .sum()
                    .reset_index()
                )

                trend["_date"] = (
                    trend["_date"]
                    .astype(str)
                )

                evidence["tables"].append({
                    "type": "time_trend",
                    "date_column": date_col,
                    "metric": metric,
                    "data": trend
                        .tail(24)
                        .to_dict("records")
                })

        except Exception:
            pass

    # --------------------------------------------------------
    # 6. Numeric summaries
    # --------------------------------------------------------

    for col in numeric:

        try:

            series = _safe_numeric(
                df[col]
            ).dropna()

            if len(series) == 0:
                continue

            evidence["tables"].append({
                "type": "numeric_summary",
                "column": col,
                "count": int(series.count()),
                "mean": float(series.mean()),
                "median": float(series.median()),
                "min": float(series.min()),
                "max": float(series.max())
            })

        except Exception:
            continue

    # Remove duplicate relevant columns
    evidence["relevant_columns"] = list(
        dict.fromkeys(
            evidence["relevant_columns"]
        )
    )

    return evidence


# ============================================================
# EXACT LOCAL ANSWERS
# ============================================================

def _local_analysis(
    df: pd.DataFrame,
    question: str
) -> Optional[Dict[str, Any]]:

    if df is None or df.empty:
        return {
            "mode": "local",
            "title": "No Data Available",
            "answer": (
                "There is no uploaded data available "
                "to answer this question."
            ),
            "evidence": [],
            "table": None
        }

    q = _normalise(question)

    # --------------------------------------------------------
    # RECORD COUNT
    # --------------------------------------------------------

    if (
        "how many records" in q
        or "how many rows" in q
        or "number of records" in q
        or "number of rows" in q
    ):

        count = len(df)

        return {
            "mode": "local",
            "title": "Dataset Size",
            "answer": (
                f"The dataset contains "
                f"{_format_number(count)} records."
            ),
            "evidence": [
                f"Rows analysed: {_format_number(count)}"
            ],
            "table": None
        }

    # --------------------------------------------------------
    # MISSING VALUES
    # --------------------------------------------------------

    if (
        "missing values" in q
        or "missing data" in q
        or "null values" in q
        or "nulls" in q
    ):

        missing = int(
            df.isna().sum().sum()
        )

        return {
            "mode": "local",
            "title": "Missing Data",
            "answer": (
                f"The dataset contains "
                f"{_format_number(missing)} missing values."
            ),
            "evidence": [
                f"Missing cells: {_format_number(missing)}"
            ],
            "table": (
                df.isna()
                .sum()
                .reset_index()
                .rename(
                    columns={
                        "index": "Column",
                        0: "Missing"
                    }
                )
                .sort_values(
                    "Missing",
                    ascending=False
                )
                .head(15)
            )
        }

    # --------------------------------------------------------
    # DUPLICATES
    # --------------------------------------------------------

    if (
        "duplicate" in q
        and (
            "how many" in q
            or "number" in q
            or "count" in q
        )
    ):

        count = int(
            df.duplicated().sum()
        )

        return {
            "mode": "local",
            "title": "Duplicate Records",
            "answer": (
                f"The dataset contains "
                f"{_format_number(count)} duplicate records."
            ),
            "evidence": [
                f"Duplicate rows: {_format_number(count)}"
            ],
            "table": None
        }

    # --------------------------------------------------------
    # TOTAL / SUM
    # --------------------------------------------------------

    metric = _detect_metric(
        df,
        question
    )

    dimension = _detect_dimension(
        df,
        question
    )

    if (
        metric
        and (
            "total" in q
            or "sum" in q
            or "overall" in q
        )
    ):

        series = _safe_numeric(
            df[metric]
        ).dropna()

        if len(series):

            total = series.sum()

            return {
                "mode": "local",
                "title": f"Total {metric}",
                "answer": (
                    f"The total {metric} is "
                    f"{_format_number(total)}."
                ),
                "evidence": [
                    f"Column analysed: {metric}",
                    f"Non-null values: {len(series)}"
                ],
                "table": None
            }

    # --------------------------------------------------------
    # AVERAGE
    # --------------------------------------------------------

    if (
        metric
        and (
            "average" in q
            or "avg" in q
            or "mean" in q
        )
    ):

        series = _safe_numeric(
            df[metric]
        ).dropna()

        if len(series):

            avg = series.mean()

            # Grouped average
            if dimension:

                grouped = (
                    df.assign(
                        __metric=_safe_numeric(
                            df[metric]
                        )
                    )
                    .groupby(
                        dimension,
                        dropna=False
                    )["__metric"]
                    .mean()
                    .sort_values(
                        ascending=False
                    )
                    .reset_index()
                )

                grouped.columns = [
                    dimension,
                    f"Average {metric}"
                ]

                return {
                    "mode": "local",
                    "title": (
                        f"Average {metric} by "
                        f"{dimension}"
                    ),
                    "answer": (
                        f"The overall average "
                        f"{metric} is "
                        f"{_format_number(avg)}. "
                        f"The grouped results show how "
                        f"this varies across "
                        f"{dimension}."
                    ),
                    "evidence": [
                        f"Overall average: {_format_number(avg)}"
                    ],
                    "table": grouped.head(15)
                }

            return {
                "mode": "local",
                "title": f"Average {metric}",
                "answer": (
                    f"The average {metric} is "
                    f"{_format_number(avg)}."
                ),
                "evidence": [
                    f"Values analysed: {len(series)}"
                ],
                "table": None
            }

    # --------------------------------------------------------
    # HIGHEST / TOP
    # --------------------------------------------------------

    if (
        metric
        and dimension
        and (
            "highest" in q
            or "top" in q
            or "most" in q
            or "maximum" in q
        )
    ):

        grouped = _group_summary(
            df,
            dimension,
            metric,
            top_n=10
        )

        if not grouped.empty:

            first = grouped.iloc[0]

            return {
                "mode": "local",
                "title": (
                    f"Highest {metric} by "
                    f"{dimension}"
                ),
                "answer": (
                    f"{first[dimension]} has the "
                    f"highest {metric}, with "
                    f"{_format_number(first['total'])}."
                ),
                "evidence": [
                    f"Dimension: {dimension}",
                    f"Metric: {metric}"
                ],
                "table": grouped
            }

    # --------------------------------------------------------
    # LOWEST / BOTTOM
    # --------------------------------------------------------

    if (
        metric
        and dimension
        and (
            "lowest" in q
            or "bottom" in q
            or "least" in q
            or "minimum" in q
        )
    ):

        grouped = _group_summary(
            df,
            dimension,
            metric,
            top_n=100
        )

        if not grouped.empty:

            grouped = grouped.sort_values(
                "total",
                ascending=True
            )

            first = grouped.iloc[0]

            return {
                "mode": "local",
                "title": (
                    f"Lowest {metric} by "
                    f"{dimension}"
                ),
                "answer": (
                    f"{first[dimension]} has the "
                    f"lowest {metric}, with "
                    f"{_format_number(first['total'])}."
                ),
                "evidence": [
                    f"Dimension: {dimension}",
                    f"Metric: {metric}"
                ],
                "table": grouped.head(10)
            }

    # --------------------------------------------------------
    # CATEGORY DISTRIBUTION
    # --------------------------------------------------------

    if (
        dimension
        and (
            "distribution" in q
            or "breakdown" in q
            or "categories" in q
            or "segments" in q
        )
    ):

        counts = (
            df[dimension]
            .value_counts(
                dropna=False
            )
            .reset_index()
        )

        counts.columns = [
            dimension,
            "Count"
        ]

        counts["Percentage"] = (
            counts["Count"]
            /
            len(df)
            * 100
        ).round(2)

        return {
            "mode": "local",
            "title": (
                f"{dimension} Distribution"
            ),
            "answer": (
                f"The dataset contains "
                f"{counts.shape[0]} distinct "
                f"{dimension} groups."
            ),
            "evidence": [
                f"Dimension analysed: {dimension}"
            ],
            "table": counts.head(15)
        }

    # --------------------------------------------------------
    # CORRELATION
    # --------------------------------------------------------

    if (
        "correlation" in q
        or "relationship between" in q
    ):

        numeric = _numeric_columns(df)

        # Try explicit columns
        mentioned = []

        for col in numeric:

            if _normalise(col) in q:
                mentioned.append(col)

        if len(mentioned) >= 2:

            c1 = mentioned[0]
            c2 = mentioned[1]

            value = df[
                [c1, c2]
            ].corr().iloc[0, 1]

            if pd.notna(value):

                direction = (
                    "positive"
                    if value > 0
                    else "negative"
                    if value < 0
                    else "no"
                )

                return {
                    "mode": "local",
                    "title": "Correlation Analysis",
                    "answer": (
                        f"The correlation between "
                        f"{c1} and {c2} is "
                        f"{value:.2f}, indicating a "
                        f"{direction} relationship."
                    ),
                    "evidence": [
                        f"{c1} vs {c2}: {value:.2f}"
                    ],
                    "table": None,
                    "note": (
                        "Correlation indicates association, "
                        "not causation."
                    )
                }

    # No reliable exact calculation.
    # IMPORTANT:
    # Do NOT return the old generic error here.
    return None


# ============================================================
# GEMINI CONTEXT
# ============================================================

def _serialise_table(
    table: Any
) -> Any:

    if isinstance(table, pd.DataFrame):

        temp = table.copy()

        for col in temp.columns:

            if pd.api.types.is_datetime64_any_dtype(
                temp[col]
            ):
                temp[col] = temp[col].astype(str)

        return temp.head(20).to_dict(
            orient="records"
        )

    return table


def _build_ai_context(
    df: pd.DataFrame,
    question: str,
    target: Optional[str] = None
) -> Dict[str, Any]:

    quality = _data_quality_summary(df)

    numeric = _numeric_columns(df)

    categorical = _categorical_columns(df)

    dates = _date_columns(df)

    evidence = _build_question_evidence(
        df,
        question,
        target
    )

    numeric_summary = {}

    for col in numeric:

        try:

            series = _safe_numeric(
                df[col]
            ).dropna()

            if len(series):

                numeric_summary[col] = {
                    "count": int(series.count()),
                    "mean": round(
                        float(series.mean()),
                        3
                    ),
                    "median": round(
                        float(series.median()),
                        3
                    ),
                    "min": round(
                        float(series.min()),
                        3
                    ),
                    "max": round(
                        float(series.max()),
                        3
                    )
                }

        except Exception:
            pass

    categorical_summary = {}

    for col in categorical:

        try:

            values = (
                df[col]
                .value_counts(
                    dropna=False
                )
                .head(15)
            )

            categorical_summary[col] = {
                str(k): int(v)
                for k, v in values.items()
            }

        except Exception:
            pass

    # Sample rows help AI understand relationships
    sample = (
        df
        .head(25)
        .copy()
    )

    sample = sample.replace(
        {
            np.nan: None,
            np.inf: None,
            -np.inf: None
        }
    )

    sample_records = sample.to_dict(
        orient="records"
    )

    # Keep evidence compact
    cleaned_tables = []

    for item in evidence.get(
        "tables",
        []
    ):

        copied = dict(item)

        if "data" in copied:
            copied["data"] = _serialise_table(
                copied["data"]
            )

        cleaned_tables.append(
            copied
        )

    return {
        "domain": evidence["domain"],
        "question": question,
        "row_count": quality["rows"],
        "column_count": quality["columns"],
        "missing_values": quality[
            "missing_values"
        ],
        "duplicate_rows": quality[
            "duplicate_rows"
        ],
        "columns": [
            str(c)
            for c in df.columns
        ],
        "numeric_columns": numeric,
        "categorical_columns": categorical,
        "date_columns": dates,
        "numeric_summary": numeric_summary,
        "categorical_summary": categorical_summary,
        "question_specific_evidence": cleaned_tables,
        "relevant_columns": evidence[
            "relevant_columns"
        ],
        "sample_rows": sample_records
    }


# ============================================================
# GEMINI CALL
# ============================================================

def _ask_gemini(
    context: Dict[str, Any]
) -> Dict[str, Any]:

    api_key = (
        os.getenv("GEMINI_API_KEY")
        or os.getenv("GOOGLE_API_KEY")
    )

    if not api_key:

        return {
            "success": False,
            "error": (
                "GEMINI_API_KEY is not configured. "
                "Add GEMINI_API_KEY to your .env file."
            )
        }

    try:

        from google import genai

    except Exception as exc:

        return {
            "success": False,
            "error": (
                "google-genai is not installed. "
                "Run: pip install -U google-genai"
            )
        }

    model_name = os.getenv(
        "GEMINI_MODEL",
        "gemini-2.5-flash"
    )

    system_instruction = """
You are the Business Intelligence analyst inside an
automated data analysis application.

Your job is to answer the user's business question using
ONLY the supplied dataset context and calculated evidence.

STRICT RULES:

1. Never invent a number.
2. Never invent a column.
3. Never claim a relationship that is not supported by the data.
4. Use the question-specific evidence whenever available.
5. If grouped evidence is available, use it.
6. If the question asks about association, do not claim causation.
7. If the data is insufficient, clearly explain what cannot be
   determined.
8. Do not answer with generic advice when the question asks for
   a data answer.
9. Give actual values from the supplied evidence.
10. Explain the result in simple business language.
11. Mention the important evidence behind the answer.
12. If there are multiple relevant dimensions, compare them.
13. For percentages, preserve the calculated percentage.
14. Do not pretend that sample rows represent the entire dataset.
15. Do not use outside knowledge to create dataset values.

Return ONLY valid JSON in this structure:

{
  "title": "Short business title",
  "answer": "Direct answer to the question using actual data",
  "evidence": [
    "Important calculated evidence",
    "Another important evidence"
  ],
  "business_interpretation": "What this means for the business",
  "limitation": "Important limitation, if any"
}

The answer should be concise but useful.
"""

    prompt = (
        system_instruction
        + "\n\nDATASET CONTEXT:\n"
        + json.dumps(
            context,
            default=str,
            ensure_ascii=False
        )
    )

    try:

        client = genai.Client(
            api_key=api_key
        )

        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config={
                "temperature": 0.1,
                "response_mime_type": "application/json"
            }
        )

        text = getattr(
            response,
            "text",
            None
        )

        if not text:

            return {
                "success": False,
                "error": "Gemini returned an empty response."
            }

        text = text.strip()

        # Remove markdown JSON fences if returned
        text = re.sub(
            r"^```json\s*",
            "",
            text,
            flags=re.IGNORECASE
        )

        text = re.sub(
            r"\s*```$",
            "",
            text
        )

        data = json.loads(text)

        return {
            "success": True,
            "data": data
        }

    except Exception as exc:

        return {
            "success": False,
            "error": str(exc)
        }


# ============================================================
# AI FALLBACK RESULT
# ============================================================

def _format_ai_result(
    ai_data: Dict[str, Any],
    context: Dict[str, Any]
) -> Dict[str, Any]:

    title = ai_data.get(
        "title",
        "Business Analysis"
    )

    answer = ai_data.get(
        "answer",
        ""
    )

    evidence = ai_data.get(
        "evidence",
        []
    )

    interpretation = ai_data.get(
        "business_interpretation",
        ""
    )

    limitation = ai_data.get(
        "limitation",
        ""
    )

    final_answer = answer

    if interpretation:

        final_answer += (
            "\n\nBusiness interpretation: "
            + interpretation
        )

    return {
        "mode": "ai",
        "title": title,
        "answer": final_answer,
        "evidence": evidence,
        "business_interpretation": interpretation,
        "limitation": limitation,
        "table": None,
        "relevant_columns": context.get(
            "relevant_columns",
            []
        )
    }


# ============================================================
# MAIN ASK DATA FUNCTION
# ============================================================

def ask_data_analyst(
    df: pd.DataFrame,
    question: str,
    target: Optional[str] = None
) -> Dict[str, Any]:

    """
    Main entry point used by the Streamlit application.

    Flow:

        User Question
              ↓
        Exact local calculation
              ↓
        Question-specific evidence
              ↓
        Gemini business interpretation
              ↓
        Final answer

    """

    # --------------------------------------------------------
    # Validation
    # --------------------------------------------------------

    if df is None:

        return {
            "mode": "error",
            "title": "No Dataset",
            "answer": (
                "Please upload a dataset before asking "
                "a question."
            ),
            "evidence": [],
            "table": None
        }

    if not isinstance(df, pd.DataFrame):

        return {
            "mode": "error",
            "title": "Invalid Dataset",
            "answer": (
                "The uploaded data could not be processed "
                "as a pandas DataFrame."
            ),
            "evidence": [],
            "table": None
        }

    if df.empty:

        return {
            "mode": "error",
            "title": "Empty Dataset",
            "answer": (
                "The uploaded dataset contains no records."
            ),
            "evidence": [],
            "table": None
        }

    if not question or not str(question).strip():

        return {
            "mode": "error",
            "title": "Question Required",
            "answer": (
                "Please enter a business question."
            ),
            "evidence": [],
            "table": None
        }

    question = str(question).strip()

    # --------------------------------------------------------
    # FIRST: exact calculation
    # --------------------------------------------------------

    try:

        local_result = _local_analysis(
            df,
            question
        )

        if local_result is not None:

            return local_result

    except Exception as exc:

        local_result = None

    # --------------------------------------------------------
    # SECOND: build question-specific evidence
    # --------------------------------------------------------

    try:

        context = _build_ai_context(
            df,
            question,
            target
        )

    except Exception as exc:

        return {
            "mode": "error",
            "title": "Analysis Error",
            "answer": (
                "The application could not prepare the "
                "uploaded data for this question."
            ),
            "evidence": [
                str(exc)
            ],
            "table": None
        }

    # --------------------------------------------------------
    # THIRD: AI interpretation
    # --------------------------------------------------------

    ai_result = _ask_gemini(
        context
    )

    if ai_result.get("success"):

        result = _format_ai_result(
            ai_result["data"],
            context
        )

        # Attach a compact evidence table when useful
        tables = context.get(
            "question_specific_evidence",
            []
        )

        if tables:

            for table in tables:

                if (
                    table.get("type")
                    in [
                        "group_metric",
                        "target_rate_by_dimension"
                    ]
                    and table.get("data")
                ):

                    try:

                        result["table"] = pd.DataFrame(
                            table["data"]
                        )

                        break

                    except Exception:
                        pass

        return result

    # --------------------------------------------------------
    # FOURTH: AI unavailable
    # --------------------------------------------------------

    error = ai_result.get(
        "error",
        "Unknown AI error"
    )

    return {
        "mode": "ai_unavailable",
        "title": "AI Analysis Unavailable",
        "answer": (
            "This question requires broader business "
            "interpretation than the built-in calculations "
            "can provide, but the AI analysis service is "
            "currently unavailable."
        ),
        "evidence": [
            f"Domain detected: {context.get('domain')}",
            (
                "Relevant columns: "
                + ", ".join(
                    context.get(
                        "relevant_columns",
                        []
                    )
                )
            ),
            f"AI service: {error}"
        ],
        "table": None,
        "relevant_columns": context.get(
            "relevant_columns",
            []
        )
    }


# ============================================================
# PROFESSIONAL SUGGESTED QUESTIONS
# ============================================================

def generate_basic_questions(
    df: pd.DataFrame,
    limit: int = 15
) -> List[str]:

    """
    Generates professional business-analysis questions
    based on the uploaded dataset.
    """

    if df is None or df.empty:
        return []

    domain = _detect_domain(df)

    columns = [
        str(c)
        for c in df.columns
    ]

    numeric = _numeric_columns(df)

    categorical = _categorical_columns(df)

    questions = []

    # --------------------------------------------------------
    # FINANCE / LOAN
    # --------------------------------------------------------

    if "Finance" in domain:

        questions.extend([
            "Which customer segments show the highest loan participation?",
            "How does loan participation vary across income levels?",
            "What customer characteristics are associated with loan account ownership?",
            "Which customer groups have the highest financial product adoption?",
            "How does income relate to customer financial product ownership?",
            "Which customer characteristics distinguish customers with different loan outcomes?",
            "Which segments represent the largest potential opportunity for financial product adoption?"
        ])

    # --------------------------------------------------------
    # HR
    # --------------------------------------------------------

    elif domain == "Human Resources":

        questions.extend([
            "Which departments show the highest employee attrition?",
            "Which employee segments have the highest retention risk?",
            "How does employee attrition vary across job roles?",
            "Which employee characteristics are associated with attrition?",
            "How does job satisfaction vary across departments?",
            "Which departments show the strongest employee stability?",
            "Which employee groups may require retention-focused attention?"
        ])

    # --------------------------------------------------------
    # SALES / RETAIL
    # --------------------------------------------------------

    elif domain == "Sales / Retail":

        questions.extend([
            "Which product categories contribute the most sales?",
            "Which customer segments generate the highest revenue?",
            "How does sales performance vary across regions?",
            "Which products show the strongest business contribution?",
            "Which segments represent the largest sales opportunity?",
            "How does profitability vary across product categories?",
            "Which areas show potential for improving sales performance?"
        ])

    # --------------------------------------------------------
    # MARKETING
    # --------------------------------------------------------

    elif domain == "Marketing":

        questions.extend([
            "Which customer segments show the highest campaign response?",
            "How does campaign performance vary across customer groups?",
            "Which customer characteristics are associated with conversion?",
            "Which marketing channels generate the strongest response?",
            "Which customer segments represent the largest conversion opportunity?",
            "How does campaign engagement vary across customer segments?"
        ])

    # --------------------------------------------------------
    # HEALTHCARE
    # --------------------------------------------------------

    elif domain == "Healthcare":

        questions.extend([
            "Which patient groups show the highest concentration of cases?",
            "How do outcomes vary across patient segments?",
            "Which patient characteristics are associated with different outcomes?",
            "How does treatment activity vary across patient groups?",
            "Which areas show the largest concentration of healthcare activity?"
        ])

    # --------------------------------------------------------
    # EDUCATION
    # --------------------------------------------------------

    elif domain == "Education":

        questions.extend([
            "Which student groups show the strongest academic performance?",
            "How does performance vary across student segments?",
            "Which student characteristics are associated with academic outcomes?",
            "How does attendance relate to academic performance?",
            "Which student groups may require additional academic support?"
        ])

    # --------------------------------------------------------
    # MANUFACTURING
    # --------------------------------------------------------

    elif domain == "Manufacturing":

        questions.extend([
            "Which production areas show the highest defect levels?",
            "Which product or machine groups have the greatest operational risk?",
            "How does production performance vary across categories?",
            "Which factors are associated with higher defect rates?",
            "Which areas represent the largest opportunity for operational improvement?"
        ])

    # --------------------------------------------------------
    # TELECOM
    # --------------------------------------------------------

    elif domain == "Telecom":

        questions.extend([
            "Which customer segments show the highest churn?",
            "Which customer characteristics are associated with churn?",
            "How does churn vary across service types?",
            "Which customer groups represent the highest retention opportunity?",
            "Which service characteristics are associated with customer retention?"
        ])

    # --------------------------------------------------------
    # GENERIC BUSINESS ANALYTICS
    # --------------------------------------------------------

    else:

        # Try to create questions using real columns
        if categorical and numeric:

            dim = categorical[0]
            metric = numeric[0]

            questions.extend([
                f"Which {dim} groups contribute the most {metric}?",
                f"How does {metric} vary across {dim}?",
                f"Which {dim} segments show the strongest business performance?",
                f"Which {dim} groups represent the largest opportunity?",
                f"Are there meaningful differences in {metric} across {dim}?"
            ])

        elif numeric:

            metric = numeric[0]

            questions.extend([
                f"What are the main patterns in {metric}?",
                f"Which factors are most closely associated with {metric}?",
                f"Are there significant variations in {metric} across the dataset?"
            ])

        elif categorical:

            dim = categorical[0]

            questions.extend([
                f"Which {dim} segments represent the largest groups?",
                f"How is the dataset distributed across {dim}?",
                f"Which {dim} segments may require further investigation?"
            ])

    # --------------------------------------------------------
    # ADD DATASET-SPECIFIC QUESTIONS
    # --------------------------------------------------------

    # Explicit category dimensions
    for col in categorical[:5]:

        normal = _normalise(col)

        if normal in [
            "department",
            "region",
            "category",
            "product",
            "segment",
            "gender"
        ]:

            questions.append(
                f"How does business performance vary across {col}?"
            )

    # Date trend
    dates = _date_columns(df)

    if dates and numeric:

        questions.append(
            f"How does {numeric[0]} change over time?"
        )

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    final = []

    seen = set()

    for question in questions:

        key = _normalise(question)

        if (
            key
            and key not in seen
        ):

            seen.add(key)
            final.append(question)

    return final[:limit]


# ============================================================
# COMPATIBILITY ALIASES
# ============================================================

def answer_question(
    df: pd.DataFrame,
    question: str,
    target: Optional[str] = None
) -> Dict[str, Any]:

    """
    Backward-compatible alias used by older app.py versions.
    """

    return ask_data_analyst(
        df=df,
        question=question,
        target=target
    )


# ============================================================
# OPTIONAL SIMPLE INSIGHT FUNCTION
# ============================================================

def generate_data_insights(
    df: pd.DataFrame,
    limit: int = 5
) -> List[str]:

    """
    Lightweight dataset-level insights.
    Useful if another part of app.py imports this function.
    """

    if df is None or df.empty:
        return []

    insights = []

    numeric = _numeric_columns(df)

    categorical = _categorical_columns(df)

    # Highest categorical concentration
    for col in categorical[:5]:

        try:

            counts = df[col].value_counts(
                dropna=False
            )

            if len(counts) >= 2:

                top_value = counts.index[0]

                top_count = counts.iloc[0]

                percentage = (
                    top_count
                    /
                    len(df)
                    *
                    100
                )

                insights.append(
                    f"{col}: {top_value} represents "
                    f"{percentage:.1f}% of records."
                )

        except Exception:
            pass

    # Numeric ranges
    for col in numeric[:5]:

        try:

            series = _safe_numeric(
                df[col]
            ).dropna()

            if len(series):

                insights.append(
                    f"{col}: average is "
                    f"{_format_number(series.mean())}, "
                    f"with values ranging from "
                    f"{_format_number(series.min())} "
                    f"to {_format_number(series.max())}."
                )

        except Exception:
            pass

    return insights[:limit]


# ============================================================
# END OF FILE
# ============================================================