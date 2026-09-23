"""Power BI-style cross-filtering helpers for the Automated BI dashboard."""

from __future__ import annotations

from typing import Any

import pandas as pd


def ensure_filter_state(st, sheet_index: int) -> dict[str, Any]:
    """Create and return the filter dictionary for one dashboard sheet."""
    if "dashboard_filters" not in st.session_state:
        st.session_state.dashboard_filters = {}

    st.session_state.dashboard_filters.setdefault(sheet_index, {})
    return st.session_state.dashboard_filters[sheet_index]


def clear_sheet_filters(st, sheet_index: int) -> None:
    """Clear all cross-filters for one dashboard sheet."""
    if "dashboard_filters" in st.session_state:
        st.session_state.dashboard_filters[sheet_index] = {}


def apply_filters(df: pd.DataFrame, filters: dict[str, Any]) -> pd.DataFrame:
    """Return a filtered copy without modifying the original dataframe."""
    if df is None or df.empty or not filters:
        return df

    result = df.copy()

    for column, value in filters.items():
        if column not in result.columns:
            continue

        values = value if isinstance(value, (list, tuple, set)) else [value]
        values = [v for v in values if v is not None]

        if not values:
            continue

        # Preserve missing-value filtering when a chart point represents NaN.
        non_null_values = [v for v in values if not pd.isna(v)]
        wants_null = len(non_null_values) != len(values)

        mask = result[column].isin(non_null_values) if non_null_values else False
        if wants_null:
            mask = mask | result[column].isna()

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
            selection = event.get("selection", {})
        except Exception:
            return []

    if selection is None:
        return []

    try:
        points = selection.points
    except Exception:
        try:
            points = selection.get("points", [])
        except Exception:
            points = []

    return list(points or [])


def _point_value(point: dict[str, Any]) -> Any:
    """Get the most reliable category value from a Plotly point."""
    customdata = point.get("customdata")

    # Our charts can optionally put the category value first in customdata.
    if isinstance(customdata, (list, tuple)) and customdata:
        return customdata[0]

    # Pie charts normally expose the category as label.
    if point.get("label") is not None:
        return point.get("label")

    # Bar/line/scatter charts normally expose the category on x or y.
    if point.get("x") is not None:
        return point.get("x")

    if point.get("y") is not None:
        return point.get("y")

    return None


def capture_chart_selection(
    st,
    event,
    category: str | None,
    sheet_index: int,
) -> bool:
    """Store a selected chart category as a sheet-level cross-filter.

    Returns True only when the filter actually changed.
    """
    if not category:
        return False

    points = _event_points(event)
    if not points:
        return False

    value = _point_value(points[0])
    if value is None:
        return False

    # Convert numpy/pandas scalar values into ordinary Python values where possible.
    try:
        value = value.item()
    except Exception:
        pass

    filters = ensure_filter_state(st, sheet_index)
    old_value = filters.get(category)

    try:
        same = bool(pd.isna(old_value) and pd.isna(value))
    except Exception:
        same = False

    if not same and old_value == value:
        same = True

    if same:
        return False

    filters[category] = value
    return True


def get_filter_summary(filters: dict[str, Any]) -> str:
    if not filters:
        return "No filters selected"

    parts = []
    for column, value in filters.items():
        parts.append(f"{column}: {value}")

    return " • ".join(parts)


def add_selection_metadata(fig, category: str | None):
    """Add category metadata to Plotly traces so Streamlit can identify selections."""
    if fig is None or not category:
        return fig

    for trace in fig.data:
        try:
            trace_type = getattr(trace, "type", "")

            if trace_type == "pie":
                labels = list(trace.labels) if trace.labels is not None else []
                trace.customdata = [[label] for label in labels]
                continue

            # Horizontal bar charts use y as the categorical axis.
            orientation = getattr(trace, "orientation", None)
            if orientation == "h":
                categories = list(trace.y) if trace.y is not None else []
            else:
                categories = list(trace.x) if trace.x is not None else []

            if categories:
                trace.customdata = [[value] for value in categories]
        except Exception:
            # A chart that cannot accept metadata should still render normally.
            continue

    return fig
