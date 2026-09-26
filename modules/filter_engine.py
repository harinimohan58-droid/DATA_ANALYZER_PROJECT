"""
Tableau / Power BI style cross-filter engine.

Behavior:
- Every dashboard sheet has its own filters.
- Clicking a chart value filters the whole current sheet.
- Multiple selections use AND logic.
- Clicking the same value again removes that filter.
- Selecting a value from another chart adds another filter.
- All charts are rebuilt from the filtered dataframe.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


# ============================================================
# FILTER STATE
# ============================================================

def ensure_filter_state(st, sheet_index: int) -> dict[str, Any]:
    """
    Get the independent filter dictionary for one dashboard sheet.
    """

    if "dashboard_filters" not in st.session_state:
        st.session_state.dashboard_filters = {}

    st.session_state.dashboard_filters.setdefault(
        sheet_index,
        {}
    )

    return st.session_state.dashboard_filters[sheet_index]


def clear_sheet_filters(
    st,
    sheet_index: int
) -> None:
    """
    Clear filters for only the selected sheet.
    """

    if "dashboard_filters" not in st.session_state:
        st.session_state.dashboard_filters = {}

    st.session_state.dashboard_filters[sheet_index] = {}


def clear_all_filters(st) -> None:
    """
    Clear filters from every sheet.
    """

    st.session_state.dashboard_filters = {}


def remove_sheet_filter(
    st,
    sheet_index: int,
    column: str
) -> None:
    """
    Remove one filter from one sheet.
    """

    filters = ensure_filter_state(
        st,
        sheet_index
    )

    filters.pop(
        column,
        None
    )


# ============================================================
# SAFE VALUE HELPERS
# ============================================================

def _is_missing(
    value: Any
) -> bool:

    try:

        result = pd.isna(value)

        if hasattr(
            result,
            "__len__"
        ):
            return False

        return bool(result)

    except Exception:
        return False


def _values_equal(
    first: Any,
    second: Any
) -> bool:

    if (
        _is_missing(first)
        and
        _is_missing(second)
    ):
        return True

    try:

        result = first == second

        if hasattr(
            result,
            "__len__"
        ):
            return False

        return bool(result)

    except Exception:
        return False


# ============================================================
# DATA TYPE CONVERSION
# ============================================================

def _coerce_to_column_dtype(
    df: pd.DataFrame | None,
    column: str | None,
    value: Any
) -> Any:

    if (
        df is None
        or not column
        or column not in df.columns
        or value is None
    ):
        return value

    if _is_missing(value):
        return value

    series = df[column]

    try:

        # -----------------------------
        # DATETIME
        # -----------------------------

        if pd.api.types.is_datetime64_any_dtype(
            series
        ):

            converted = pd.to_datetime(
                value,
                errors="coerce"
            )

            if not pd.isna(converted):
                return converted

        # -----------------------------
        # NUMERIC
        # -----------------------------

        if pd.api.types.is_numeric_dtype(
            series
        ):

            converted = pd.to_numeric(
                value,
                errors="coerce"
            )

            if not pd.isna(converted):

                if pd.api.types.is_integer_dtype(
                    series
                ):

                    try:
                        return int(converted)
                    except Exception:
                        pass

                return converted

        # -----------------------------
        # BOOLEAN
        # -----------------------------

        if pd.api.types.is_bool_dtype(
            series
        ):

            if isinstance(
                value,
                str
            ):

                text = (
                    value
                    .strip()
                    .lower()
                )

                if text in {
                    "true",
                    "yes",
                    "1"
                }:
                    return True

                if text in {
                    "false",
                    "no",
                    "0"
                }:
                    return False

    except Exception:
        pass

    try:
        return value.item()
    except Exception:
        return value


# ============================================================
# APPLY ALL FILTERS
# ============================================================

def apply_filters(
    df: pd.DataFrame,
    filters: dict[str, Any]
) -> pd.DataFrame:

    """
    Apply ALL active filters using AND logic.

    Example:

        Department = Sales
        AND
        Gender = Female
        AND
        BusinessTravel = Travel_Rarely

    Every dashboard chart receives this filtered dataframe.
    """

    if (
        df is None
        or not isinstance(df, pd.DataFrame)
    ):
        return df

    if not filters:
        return df.copy()

    result = df.copy()

    for column, value in filters.items():

        if column not in result.columns:
            continue

        # Allow multiple values for future multi-selection.
        if isinstance(
            value,
            (list, tuple, set)
        ):

            selected_values = list(value)

        else:

            selected_values = [
                value
            ]

        non_null_values = [
            v
            for v in selected_values
            if not _is_missing(v)
        ]

        wants_null = (
            len(non_null_values)
            !=
            len(selected_values)
        )

        mask = pd.Series(
            False,
            index=result.index
        )

        # -----------------------------
        # NORMAL VALUES
        # -----------------------------

        if non_null_values:

            converted_values = [
                _coerce_to_column_dtype(
                    result,
                    column,
                    v
                )
                for v in non_null_values
            ]

            mask = (
                result[column]
                .isin(converted_values)
            )

        # -----------------------------
        # MISSING VALUES
        # -----------------------------

        if wants_null:

            mask = (
                mask
                |
                result[column].isna()
            )

        result = result.loc[mask]

    return result.copy()


# ============================================================
# STREAMLIT PLOTLY EVENT
# ============================================================

def _event_points(event) -> list[dict[str, Any]]:

    if event is None:
        return []

    try:

        selection = event.selection

    except Exception:

        try:
            selection = event.get(
                "selection",
                {}
            )

        except Exception:
            return []

    if selection is None:
        return []

    try:

        points = selection.points

    except Exception:

        try:
            points = selection.get(
                "points",
                []
            )

        except Exception:
            points = []

    return list(
        points or []
    )


# ============================================================
# EXTRACT SELECTED VALUE
# ============================================================

def _point_value(
    point: dict[str, Any]
) -> Any:

    customdata = point.get(
        "customdata"
    )

    # Our metadata:
    #
    # [column_name, selected_value]
    #
    if (
        isinstance(
            customdata,
            (list, tuple)
        )
        and
        len(customdata) >= 2
    ):

        return customdata[1]

    # Fallback.
    if (
        isinstance(
            customdata,
            (list, tuple)
        )
        and
        len(customdata) >= 1
    ):

        return customdata[0]

    # Pie.
    if point.get("label") is not None:
        return point.get("label")

    # X value.
    if point.get("x") is not None:
        return point.get("x")

    # Y value.
    if point.get("y") is not None:
        return point.get("y")

    return None


# ============================================================
# CAPTURE CHART SELECTION
# ============================================================

def capture_chart_selection(
    st,
    event,
    category: str | None,
    sheet_index: int,
    df: pd.DataFrame | None = None,
    filter_column: str | None = None,
) -> bool:

    """
    Convert a Plotly chart selection into a sheet-level filter.

    Example:

        Click:
            Department = Sales

        Stored as:
            {
                "Department": "Sales"
            }

        Next click:

            Gender = Female

        Stored as:
            {
                "Department": "Sales",
                "Gender": "Female"
            }

        Result:

            Department == Sales
            AND
            Gender == Female
    """

    points = _event_points(
        event
    )

    if not points:
        return False

    # We use the first selected point.
    point = points[0]

    # --------------------------------------------------------
    # FIND FILTER COLUMN
    # --------------------------------------------------------

    selected_column = (
        filter_column
        or category
    )

    customdata = point.get(
        "customdata"
    )

    # Our metadata stores:
    #
    # [column, value]
    #
    if (
        isinstance(
            customdata,
            (list, tuple)
        )
        and
        len(customdata) >= 2
    ):

        metadata_column = customdata[0]

        if (
            df is not None
            and
            metadata_column in df.columns
        ):

            selected_column = (
                metadata_column
            )

    if not selected_column:
        return False

    # --------------------------------------------------------
    # FIND VALUE
    # --------------------------------------------------------

    value = _point_value(
        point
    )

    if value is None:
        return False

    # --------------------------------------------------------
    # CONVERT VALUE
    # --------------------------------------------------------

    value = _coerce_to_column_dtype(
        df,
        selected_column,
        value
    )

    # --------------------------------------------------------
    # CURRENT FILTERS
    # --------------------------------------------------------

    filters = ensure_filter_state(
        st,
        sheet_index
    )

    old_value = filters.get(
        selected_column
    )

    # ========================================================
    # TABLEAU STYLE TOGGLE
    # ========================================================

    # Clicking the same selected value again
    # removes that filter.

    if _values_equal(
        old_value,
        value
    ):

        filters.pop(
            selected_column,
            None
        )

        return True

    # ========================================================
    # ADD / REPLACE FILTER
    # ========================================================

    filters[selected_column] = value

    return True


# ============================================================
# FILTER SUMMARY
# ============================================================

def get_filter_summary(
    filters: dict[str, Any]
) -> str:

    if not filters:
        return "No filters selected"

    parts = []

    for column, value in filters.items():

        if _is_missing(value):
            display_value = "Missing"
        else:
            display_value = str(value)

        parts.append(
            f"{column}: {display_value}"
        )

    return " • ".join(
        parts
    )


# ============================================================
# PLOTLY SELECTION METADATA
# ============================================================

def add_selection_metadata(
    fig,
    category: str | None,
    df: pd.DataFrame | None = None,
    metric: str | None = None,
    chart_type: str | None = None,
):

    """
    Attach [column, value] metadata to EVERY selectable trace.

    Supported:
        Bar
        Horizontal Bar
        Line
        Area
        Pie
        Scatter
        Box
        Violin
        Other categorical traces

    Histogram:
        handled separately because histogram bars represent
        ranges rather than individual dataframe values.
    """

    if fig is None:
        return fig

    for trace in fig.data:

        try:

            trace_type = getattr(
                trace,
                "type",
                ""
            )

            orientation = getattr(
                trace,
                "orientation",
                None
            )

            # =================================================
            # PIE
            # =================================================

            if trace_type == "pie":

                labels = (
                    list(trace.labels)
                    if trace.labels is not None
                    else []
                )

                if category and labels:

                    trace.customdata = [
                        [
                            category,
                            value
                        ]
                        for value in labels
                    ]

                continue

            # =================================================
            # HISTOGRAM
            # =================================================

            if trace_type == "histogram":

                # Histogram bars represent ranges.
                # Do not treat the bin as an exact row value.
                #
                # It remains selectable visually, but the
                # histogram requires range-filter handling
                # when range selection is implemented.

                continue

            # =================================================
            # CATEGORY / DIMENSION CHART
            # =================================================

            if category:

                if orientation == "h":

                    values = (
                        list(trace.y)
                        if trace.y is not None
                        else []
                    )

                else:

                    values = (
                        list(trace.x)
                        if trace.x is not None
                        else []
                    )

                if values:

                    trace.customdata = [
                        [
                            category,
                            value
                        ]
                        for value in values
                    ]

                continue

            # =================================================
            # METRIC-ONLY CHART
            # =================================================

            if not metric:
                continue

            if orientation == "h":

                values = (
                    list(trace.x)
                    if trace.x is not None
                    else []
                )

            else:

                values = (
                    list(trace.y)
                    if trace.y is not None
                    else []
                )

            if values:

                trace.customdata = [
                    [
                        metric,
                        value
                    ]
                    for value in values
                ]

        except Exception:

            # One unusual Plotly trace should never break
            # the entire dashboard.
            continue

    return fig