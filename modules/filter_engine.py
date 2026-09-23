"""Power BI-style cross-filtering helpers for the Automated BI dashboard."""

from __future__ import annotations

from typing import Any

import pandas as pd


def ensure_filter_state(
    st,
    sheet_index: int
) -> dict[str, Any]:
    """Create and return the filter dictionary for one dashboard sheet."""

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
    """Clear all cross-filters for one dashboard sheet."""

    if "dashboard_filters" in st.session_state:
        st.session_state.dashboard_filters[sheet_index] = {}


def apply_filters(
    df: pd.DataFrame,
    filters: dict[str, Any]
) -> pd.DataFrame:
    """
    Apply all active filters to the dataframe.

    Filters are combined using AND logic.
    """

    if df is None or df.empty or not filters:
        return df

    result = df.copy()

    for column, value in filters.items():

        if column not in result.columns:
            continue

        values = (
            value
            if isinstance(
                value,
                (list, tuple, set)
            )
            else [value]
        )

        values = [
            v
            for v in values
            if v is not None
        ]

        if not values:
            continue

        non_null_values = []
        wants_null = False

        for value_item in values:

            try:

                if pd.isna(value_item):
                    wants_null = True
                else:
                    non_null_values.append(
                        value_item
                    )

            except Exception:

                non_null_values.append(
                    value_item
                )

        if non_null_values:

            mask = result[column].isin(
                non_null_values
            )

        else:

            mask = pd.Series(
                False,
                index=result.index
            )

        if wants_null:

            mask = (
                mask
                | result[column].isna()
            )

        result = result.loc[mask]

    return result.copy()


def _event_points(event) -> list[dict[str, Any]]:
    """Safely extract Plotly selection points from a Streamlit event."""

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

    return list(points or [])


def _point_value(
    point: dict[str, Any]
) -> Any:
    """Get the most reliable category value from a Plotly point."""

    customdata = point.get(
        "customdata"
    )

    if isinstance(
        customdata,
        (list, tuple)
    ):

        if customdata:
            return customdata[0]

    elif customdata is not None:

        return customdata

    if point.get("label") is not None:
        return point.get("label")

    if point.get("x") is not None:
        return point.get("x")

    if point.get("y") is not None:
        return point.get("y")

    return None


def _coerce_to_column_dtype(
    df: pd.DataFrame | None,
    column: str,
    value: Any
) -> Any:
    """
    Convert Plotly-selected values to the
    datatype used by the dataframe column.
    """

    if (
        df is None
        or column not in df.columns
        or value is None
    ):
        return value

    try:

        if pd.isna(value):
            return value

    except Exception:
        pass

    series = df[column]

    try:

        if pd.api.types.is_datetime64_any_dtype(
            series
        ):

            converted = pd.to_datetime(
                value,
                errors="coerce"
            )

            if not pd.isna(converted):
                return converted

        if pd.api.types.is_numeric_dtype(
            series
        ):

            converted = pd.to_numeric(
                value,
                errors="coerce"
            )

            if not pd.isna(converted):
                return converted

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
                    "1",
                }:
                    return True

                if text in {
                    "false",
                    "no",
                    "0",
                }:
                    return False

    except Exception:
        pass

    try:
        return value.item()

    except Exception:
        return value


def _values_equal(
    first: Any,
    second: Any
) -> bool:
    """Safely compare two filter values."""

    try:

        result = first == second

        if isinstance(
            result,
            bool
        ):
            return result

        return bool(result)

    except Exception:

        return False


def capture_chart_selection(
    st,
    event,
    category: str | None,
    sheet_index: int,
    df: pd.DataFrame | None = None
) -> bool:
    """
    Store a selected chart category as a
    sheet-level cross-filter.

    Returns True only when the filter changed.
    """

    if not category:
        return False

    points = _event_points(event)

    if not points:
        return False

    value = _point_value(
        points[0]
    )

    if value is None:
        return False

    value = _coerce_to_column_dtype(
        df,
        category,
        value
    )

    filters = ensure_filter_state(
        st,
        sheet_index
    )

    old_value = filters.get(
        category
    )

    try:

        if (
            pd.isna(old_value)
            and pd.isna(value)
        ):
            return False

    except Exception:
        pass

    if _values_equal(
        old_value,
        value
    ):
        return False

    filters[category] = value

    return True


def get_filter_summary(
    filters: dict[str, Any]
) -> str:
    """Create a readable dashboard filter summary."""

    if not filters:
        return "No filters selected"

    parts = []

    for column, value in filters.items():

        try:

            if pd.isna(value):
                display_value = "Missing"

            else:
                display_value = str(value)

        except Exception:

            display_value = str(value)

        parts.append(
            f"{column}: {display_value}"
        )

    return " • ".join(parts)


def add_selection_metadata(
    fig,
    category: str | None
):
    """
    Add category metadata to Plotly traces.

    This allows Streamlit to identify which
    category the user clicked.
    """

    if (
        fig is None
        or not category
    ):
        return fig

    for trace in fig.data:

        try:

            trace_type = getattr(
                trace,
                "type",
                ""
            )

            # PIE CHART
            if trace_type == "pie":

                labels = (
                    list(trace.labels)
                    if trace.labels is not None
                    else []
                )

                trace.customdata = [
                    [label]
                    for label in labels
                ]

                continue

            # BAR / LINE / OTHER CHARTS
            orientation = getattr(
                trace,
                "orientation",
                None
            )

            if orientation == "h":

                categories = (
                    list(trace.y)
                    if trace.y is not None
                    else []
                )

            else:

                categories = (
                    list(trace.x)
                    if trace.x is not None
                    else []
                )

            if categories:

                trace.customdata = [
                    [value]
                    for value in categories
                ]

        except Exception:

            # The chart should still render even
            # if a trace does not accept metadata.
            continue

    return fig
