from pathlib import Path
import pickle

import streamlit as st

from modules.chart_engine import create_chart
from modules.filter_engine import (
    ensure_filter_state,
    apply_filters,
    capture_chart_selection,
    clear_sheet_filters,
    get_filter_summary,
    add_selection_metadata,
)

PROJECT_DIR = Path(__file__).resolve().parent
SNAPSHOT_PATH = PROJECT_DIR / "reports" / "dashboard_snapshot.pkl"

st.set_page_config(
    page_title="Dashboard",
    page_icon="📊",
    layout="wide"
)


def load_snapshot():
    if not SNAPSHOT_PATH.exists():
        return None, []

    with open(SNAPSHOT_PATH, "rb") as f:
        snapshot = pickle.load(f)

    return snapshot.get("df"), snapshot.get("sheets", [])


df, sheets = load_snapshot()

if df is None or not sheets:
    st.title("📊 Business Dashboard")
    st.warning(
        "Generate the Final PDF from the main application first."
    )
    st.stop()


st.title("📊 Business Dashboard")

st.caption(
    f"{len(sheets)} dashboard sheets • "
    f"{sum(len(s.get('charts', [])) for s in sheets)} charts • "
    f"{len(df):,} records"
)

st.divider()


sheet_tabs = st.tabs(
    [
        s.get("name", f"Sheet {i + 1}")
        for i, s in enumerate(sheets)
    ]
)


for sheet_index, (sheet_tab, sheet) in enumerate(
    zip(sheet_tabs, sheets)
):

    with sheet_tab:

        st.subheader(
            f"📁 {sheet.get('name', f'Sheet {sheet_index + 1}')}"
        )

        if sheet.get("description"):
            st.caption(sheet["description"])

        charts = sorted(
            sheet.get("charts", []),
            key=lambda c: c.get("position", 999)
        )

        # ==================================================
        # POWER BI-STYLE CROSS-FILTERING
        # ==================================================

        sheet_filters = ensure_filter_state(
            st,
            sheet_index
        )

        filter_col1, filter_col2 = st.columns([5, 1])

        with filter_col1:

            if sheet_filters:

                st.info(
                    "🔎 Active dashboard filter: "
                    + get_filter_summary(sheet_filters)
                )

            else:

                st.caption(
                    "💡 Click a category in any chart to filter "
                    "the entire dashboard sheet."
                )

        with filter_col2:

            if st.button(
                "✖ Clear Filters",
                key=f"standalone_clear_filters_{sheet_index}",
                use_container_width=True,
                disabled=not bool(sheet_filters)
            ):

                clear_sheet_filters(
                    st,
                    sheet_index
                )

                st.rerun()

        filtered_df = apply_filters(
            df,
            sheet_filters
        )

        st.caption(
            f"Showing {len(filtered_df):,} of {len(df):,} records"
        )

        columns = st.columns(2)

        for display_index, chart in enumerate(charts):

            with columns[display_index % 2]:

                try:

                    category = chart.get("category")

                    fig = create_chart(
                        filtered_df,
                        category=category,
                        metric=chart.get("metric"),
                        chart_type=chart.get(
                            "chart_type",
                            "Bar"
                        ),
                        color=chart.get(
                            "color",
                            "#2563EB"
                        ),
                        title=chart.get(
                            "title",
                            "Business Chart"
                        ),
                    )

                    add_selection_metadata(
                        fig,
                        category
                    )

                    event = st.plotly_chart(
                        fig,
                        use_container_width=True,
                        key=(
                            f"standalone_"
                            f"{sheet_index}_"
                            f"{chart.get('chart_id', display_index)}"
                        ),
                        on_select="rerun",
                        selection_mode="points"
                    )

                    # IMPORTANT:
                    # Pass the original dataframe so the filter
                    # engine can convert the clicked Plotly value
                    # to the correct dataframe datatype.
                    if capture_chart_selection(
                        st,
                        event,
                        category,
                        sheet_index,
                        df=df
                    ):

                        st.rerun()

                except Exception as error:

                    st.error(
                        f"Unable to render chart: {error}"
                    )

        st.success(
            f"✅ {sheet.get('name', 'Sheet')} contains "
            f"{len(charts)} charts. "
            f"Current records: {len(filtered_df):,}."
        )


st.divider()

st.caption(
    "Standalone Dashboard • Generated from the main Automated BI Platform"
)
