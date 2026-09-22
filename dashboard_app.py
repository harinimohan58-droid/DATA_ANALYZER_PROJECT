from pathlib import Path
import pickle

import streamlit as st

from modules.chart_engine import create_chart

PROJECT_DIR = Path(__file__).resolve().parent
SNAPSHOT_PATH = PROJECT_DIR / "reports" / "dashboard_snapshot.pkl"

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

def load_snapshot():
    if not SNAPSHOT_PATH.exists():
        return None, []
    with open(SNAPSHOT_PATH, "rb") as f:
        snapshot = pickle.load(f)
    return snapshot.get("df"), snapshot.get("sheets", [])

df, sheets = load_snapshot()

if df is None or not sheets:
    st.title("📊 Business Dashboard")
    st.warning("Generate the Final PDF from the main application first.")
    st.stop()

st.title("📊 Business Dashboard")
st.caption(
    f"{len(sheets)} dashboard sheets • "
    f"{sum(len(s.get('charts', [])) for s in sheets)} charts • "
    f"{len(df):,} records"
)

st.divider()

sheet_tabs = st.tabs([
    s.get("name", f"Sheet {i + 1}") for i, s in enumerate(sheets)
])

for sheet_index, (sheet_tab, sheet) in enumerate(zip(sheet_tabs, sheets)):
    with sheet_tab:
        st.subheader(f"📁 {sheet.get('name', f'Sheet {sheet_index + 1}')}")
        if sheet.get("description"):
            st.caption(sheet["description"])

        charts = sorted(
            sheet.get("charts", []),
            key=lambda c: c.get("position", 999)
        )
        columns = st.columns(2)

        for display_index, chart in enumerate(charts):
            with columns[display_index % 2]:
                try:
                    fig = create_chart(
                        df,
                        category=chart.get("category"),
                        metric=chart.get("metric"),
                        chart_type=chart.get("chart_type", "Bar"),
                        color=chart.get("color", "#2563EB"),
                        title=chart.get("title", "Business Chart"),
                    )
                    st.plotly_chart(
                        fig,
                        use_container_width=True,
                        key=f"standalone_{sheet_index}_{chart.get('chart_id', display_index)}"
                    )
                except Exception as error:
                    st.error(f"Unable to render chart: {error}")

        st.success(f"✅ {sheet.get('name', 'Sheet')} contains {len(charts)} charts.")

st.divider()
st.caption("Standalone Dashboard • Generated from the main Automated BI Platform")
