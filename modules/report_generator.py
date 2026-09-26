import math
import os
import re
from pathlib import Path
from html import escape

import pandas as pd
from PIL import Image as PILImage, ImageDraw, ImageFont

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
    KeepTogether,
)
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from modules.chart_engine import create_chart


def _configure_kaleido_browser():
    """Point Kaleido at Streamlit Community Cloud's Chromium binary when available."""
    if os.environ.get("BROWSER_PATH"):
        return
    if os.name != "posix":
        return
    for browser in ("/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome-stable", "/usr/bin/google-chrome", "/usr/bin/chrome"):
        if os.path.exists(browser):
            os.environ["BROWSER_PATH"] = browser
            return


_configure_kaleido_browser()


# ============================================================
# SAFE / FORMATTING HELPERS
# ============================================================

def safe(value):
    if value is None:
        return "N/A"
    return str(value)


def fmt_num(value):
    try:
        x = float(value)
        if abs(x) >= 1_000_000:
            return f"{x / 1_000_000:.2f}M"
        if abs(x) >= 1_000:
            return f"{x:,.0f}"
        return f"{x:,.2f}"
    except Exception:
        return safe(value)


def pretty_column(value):
    text = re.sub(r"[_\-]+", " ", str(value))
    text = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", text)
    return re.sub(r"\s+", " ", text).strip().title()


def add_table(story, data, widths=None, font_size=7, header_bg="#163A63"):
    if not data:
        return

    page_width = A4[0]
    usable_width = page_width - 36 * mm
    max_columns = max(len(row) for row in data)
    normalized = []
    for row in data:
        row = list(row)
        row += [""] * (max_columns - len(row))
        normalized.append(row[:max_columns])

    if widths and len(widths) == max_columns:
        total = sum(float(w) for w in widths)
        if total > usable_width:
            scale = usable_width / total
            widths = [float(w) * scale for w in widths]
    else:
        widths = [usable_width / max_columns] * max_columns

    body = ParagraphStyle(
        f"TblBody{len(story)}",
        fontName="Helvetica",
        fontSize=font_size,
        leading=font_size + 2,
        wordWrap="CJK",
    )
    header = ParagraphStyle(
        f"TblHeader{len(story)}",
        parent=body,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )

    cleaned = []
    for ri, row in enumerate(normalized):
        cleaned.append([
            Paragraph(escape(safe(v)), header if ri == 0 else body)
            for v in row
        ])

    table = Table(cleaned, colWidths=widths, repeatRows=1, splitByRow=1)
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_bg)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#CBD5E1")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(table)
    story.append(Spacer(1, 7))


def _paragraph_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="ReportTitle",
        parent=styles["Title"],
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#163A63"),
        spaceAfter=10,
    ))
    styles.add(ParagraphStyle(
        name="Section",
        parent=styles["Heading1"],
        fontSize=17,
        leading=21,
        textColor=colors.HexColor("#163A63"),
        spaceAfter=8,
    ))
    styles.add(ParagraphStyle(
        name="Subsection",
        parent=styles["Heading2"],
        fontSize=11,
        leading=14,
        textColor=colors.HexColor("#245A8D"),
        spaceBefore=5,
        spaceAfter=5,
    ))
    styles.add(ParagraphStyle(
        name="Small",
        parent=styles["Normal"],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#334155"),
    ))
    styles.add(ParagraphStyle(
        name="Question",
        parent=styles["Normal"],
        fontSize=8.5,
        leading=12,
        spaceAfter=3,
    ))
    styles.add(ParagraphStyle(
        name="Link",
        parent=styles["Normal"],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#1565C0"),
        underline=True,
    ))
    return styles


def _style_neon_figure(fig, chart=None):
    """Use the exact same Plotly styling as the Streamlit dashboard."""
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
                font=dict(color="#F6FAFF", size=17),
                x=0.02,
                xanchor="left",
            ),
            margin=dict(l=35, r=20, t=55, b=50),
            hovermode="closest",
            hoverlabel=dict(
                bgcolor="#0A1730",
                bordercolor="#2B5B91",
                font=dict(color="#F7FAFF", size=12),
            ),
            legend=dict(
                font=dict(color="#AFC3DF", size=11),
                bgcolor="rgba(0,0,0,0)",
                title_text="",
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
            height=360,
        )

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

        for trace in fig.data:
            try:
                if getattr(trace, "mode", None) and "lines" in str(trace.mode):
                    trace.line.width = 3
            except Exception:
                pass
    except Exception:
        pass
    return fig


# ============================================================
# DASHBOARD COMPOSITE IMAGE
# ============================================================

def _render_dashboard_panel(df, sheet, sheet_index, output_dir):
    """Render the exact charts used by the Streamlit dashboard as one PDF panel."""
    charts = sorted(
        sheet.get("charts", []),
        key=lambda x: x.get("position", 999),
    )
    if not charts:
        return None

    tile_w, tile_h = 560, 320
    gap = 22
    header_h = 95
    cols = 2
    rows = math.ceil(len(charts) / cols)
    canvas_w = cols * tile_w + (cols + 1) * gap
    canvas_h = header_h + rows * tile_h + (rows + 1) * gap

    # The PDF panel uses the same midnight-blue visual language as Streamlit.
    canvas = PILImage.new("RGB", (canvas_w, canvas_h), "#071228")
    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 28)
        small_font = ImageFont.truetype("DejaVuSans.ttf", 17)
    except Exception:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    sheet_name = safe(sheet.get("name", f"Dashboard Sheet {sheet_index}"))
    draw.text((gap, 18), sheet_name, fill="#F6FAFF", font=font)
    draw.text(
        (gap, 55),
        f"Same Streamlit dashboard charts • {len(charts)} analytical views",
        fill="#8FB7DD",
        font=small_font,
    )

    image_dir = Path(output_dir) / "_dashboard_tiles"
    image_dir.mkdir(parents=True, exist_ok=True)

    for idx, chart in enumerate(charts):
        # IMPORTANT: no replacement/random charts. The exact chart definition
        # from st.session_state.sheets is sent through the same chart engine.
        fig = create_chart(
            df,
            category=chart.get("category"),
            metric=chart.get("metric"),
            chart_type=chart.get("chart_type", "Bar"),
            color=chart.get("color", "#22D3EE"),
            title=chart.get("title", "Business Chart"),
        )
        fig = _style_neon_figure(fig, chart)
        fig.update_layout(width=tile_w, height=tile_h)

        tile_path = image_dir / f"sheet_{sheet_index}_tile_{idx}.png"
        # Use the exact Plotly figure rendered by Streamlit. Kaleido is only
        # the image exporter needed to place that same figure in the PDF.
        try:
            fig.write_image(
                str(tile_path),
                format="png",
                width=tile_w,
                height=tile_h,
                scale=1,
            )
        except Exception as exc:
            raise RuntimeError(
                "The exact Streamlit Plotly chart could not be exported to PNG. "
                "Install/upgrade Plotly and Kaleido in the deployment environment. "
                f"Underlying error: {exc}"
            ) from exc

        tile = PILImage.open(tile_path).convert("RGB")
        x = gap + (idx % cols) * (tile_w + gap)
        y = header_h + gap + (idx // cols) * (tile_h + gap)
        canvas.paste(tile, (x, y))

    out_path = Path(output_dir) / f"dashboard_panel_{sheet_index}.png"
    canvas.save(out_path, quality=94)
    return out_path


def _dashboard_overall_summary(df, sheets):
    numeric = df.select_dtypes(include="number")
    categorical = df.select_dtypes(include=["object", "category", "bool"])
    parts = [
        f"The dashboard combines {len(sheets or []):,} analytical sheets and "
        f"{sum(len(s.get('charts', [])) for s in sheets or []):,} visual views "
        f"from {len(df):,} records."
    ]
    if not numeric.empty:
        primary = numeric.columns[0]
        s = pd.to_numeric(numeric[primary], errors="coerce").dropna()
        if not s.empty:
            parts.append(
                f"The first available numeric measure, {pretty_column(primary)}, "
                f"has an average of {fmt_num(s.mean())} and a median of {fmt_num(s.median())}."
            )
    if not categorical.empty:
        c = categorical.columns[0]
        vc = categorical[c].dropna().astype(str).value_counts()
        if not vc.empty:
            parts.append(
                f"The largest observed group in {pretty_column(c)} is "
                f"'{safe(vc.index[0])}', representing {vc.iloc[0] / max(len(categorical[c].dropna()),1) * 100:.1f}% "
                "of non-missing records."
            )
    return " ".join(parts)


def _simple_stat_summary(df):
    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        return "The dataset does not contain numeric measures suitable for a standard descriptive-statistics summary."
    rows = []
    for col in numeric.columns[:12]:
        s = pd.to_numeric(numeric[col], errors="coerce").dropna()
        if s.empty:
            continue
        rows.append({
            "Measure": pretty_column(col),
            "Average": s.mean(),
            "Median": s.median(),
            "Minimum": s.min(),
            "Maximum": s.max(),
            "Variation": s.std() if len(s) > 1 else 0,
        })
    if not rows:
        return "No usable numeric measures were available."
    widest = max(rows, key=lambda r: float(r["Maximum"]) - float(r["Minimum"]))
    return (
        f"Across the available numeric measures, {widest['Measure']} shows one of the widest observed ranges "
        f"({fmt_num(widest['Minimum'])} to {fmt_num(widest['Maximum'])}). "
        "The average and median are presented together so management can see both the typical level and the effect of unusually high or low observations. "
        "The statistics are descriptive; they do not by themselves establish cause or business impact."
    ), rows


def _management_explanation(df, question):
    """Turn a business question into a simple management-focus statement."""
    q = str(question)
    lower = q.lower()
    numeric = df.select_dtypes(include="number").columns.tolist()
    categorical = df.select_dtypes(include=["object", "category", "bool"]).columns.tolist()

    if "missing" in lower:
        return "Management should confirm whether the affected fields are complete enough for reliable reporting before using the related KPI or segment for decisions."
    if "duplicate" in lower:
        return "Management should verify whether repeated rows are genuine transactions/observations or accidental duplicates before relying on totals and counts."
    if "trend" in lower or "over" in lower:
        return "Management should monitor the movement over time, identify sustained changes rather than one-off fluctuations, and connect the change to operational actions."
    if "highest" in lower or "strongest" in lower or "contribute" in lower:
        return "Management should identify the groups driving the result, understand why they differ, and decide whether the same pattern should be protected, improved, or investigated further."
    if "relationship" in lower or "associated" in lower:
        return "Management should investigate whether the two measures move together consistently and whether the relationship is useful for targeting, planning, or forecasting. Association should not be treated as proof of causation."
    if "segment" in lower or "customer" in lower or "group" in lower:
        return "Management should compare the segments using the relevant KPI, identify materially different groups, and prioritize follow-up where the business outcome is weakest or most important."
    if numeric and categorical:
        return f"Management should compare the available business measure(s) across the main segments and focus on groups where the observed performance differs materially from the overall pattern."
    return "Management should use this question to validate the most important pattern visible in the uploaded data and convert the finding into a measurable business action."


def _research_source_lines(research_sources):
    lines = []
    for item in (research_sources or [])[:6]:
        if isinstance(item, dict):
            title = item.get("title", "Research source")
            url = item.get("url", "")
            snippet = item.get("snippet", "")
            text = f"{title}"
            if snippet:
                text += f" — {snippet}"
            if url:
                text += f" ({url})"
            lines.append(text)
        else:
            lines.append(str(item))
    return lines


# ============================================================
# MAIN PDF FUNCTION
# ============================================================

def generate_pdf(
    file_path,
    df,
    kpis,
    sheets,
    insights,
    recommendations,
    questions,
    research_result=None,
    research_sources=None,
    research_detail=None,
    user_analysis=None,
    dashboard_url=None,
):
    """Generate a compact, professional 10–15 page management report.

    Dashboard charts are the same chart definitions used by the Streamlit
    dashboard: the same sheet order, category, metric, chart type, title,
    colour and Plotly styling. They are rendered as combined sheet panels for
    the PDF; no fallback or replacement charts are generated.
    """
    document = SimpleDocTemplate(
        file_path,
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=16 * mm,
        bottomMargin=16 * mm,
        title="Automated Business Intelligence Report",
        author="Automated Business Intelligence Platform",
    )
    styles = _paragraph_styles()
    story = []
    work_dir = Path(file_path).parent / "_compact_report_assets"
    work_dir.mkdir(parents=True, exist_ok=True)

    total_charts = sum(len(s.get("charts", [])) for s in sheets or [])
    missing_total = int(df.isna().sum().sum())
    duplicate_total = int(df.duplicated().sum())
    quality = max(0, round((1 - missing_total / max(len(df) * max(len(df.columns), 1), 1)) * 100))

    # --------------------------------------------------------
    # 1. COVER / EXECUTIVE OVERVIEW
    # --------------------------------------------------------
    story.append(Spacer(1, 25))
    story.append(Paragraph("AUTOMATED BUSINESS INTELLIGENCE REPORT", styles["ReportTitle"]))
    story.append(Paragraph("Professional Management Summary", styles["Section"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        f"This report converts the uploaded dataset into a management-ready view covering "
        f"{len(df):,} records, {len(df.columns):,} fields, {len(sheets or []):,} dashboard sheets and {total_charts:,} dashboard visuals.",
        styles["Normal"],
    ))
    story.append(Spacer(1, 12))

    overview_data = [
        ["Report Area", "What management receives"],
        ["Dashboard", "One combined visual view of the generated dashboard sheets."],
        ["Statistics", "A concise explanation of scale, typical values, spread and data quality."],
        ["Business Insights", "Simple evidence-based signals, barriers and management focus areas."],
        ["Domain Research", "Plain-language explanation of the dataset's business domain and fields."],
        ["Management Questions", "All generated questions with a practical explanation of why each matters."],
    ]
    add_table(story, overview_data, widths=[45 * mm, 125 * mm], font_size=8)

    story.append(Paragraph("Executive Interpretation", styles["Subsection"]))
    story.append(Paragraph(_dashboard_overall_summary(df, sheets), styles["Normal"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        f"Data quality indicator: <b>{quality}%</b> based on missing-cell coverage. "
        f"Missing cells: <b>{missing_total:,}</b>; exact duplicate rows: <b>{duplicate_total:,}</b>.",
        styles["Normal"],
    ))
    if dashboard_url:
        href = escape(str(dashboard_url), quote=True)
        story.append(Spacer(1, 16))
        story.append(Paragraph(
            f'<link href="{href}"><u>🔗 OPEN INTERACTIVE DASHBOARD PAGE</u></link>',
            styles["Link"],
        ))
        story.append(Paragraph(
            "The link opens the same interactive dashboard inside the Streamlit application.",
            styles["Small"],
        ))
    story.append(PageBreak())

    # --------------------------------------------------------
    # 2. COMPLETE DASHBOARD — ONE PANEL PER SHEET, NO CHART-BY-CHART PAGES
    # --------------------------------------------------------
    story.append(Paragraph("1. Complete Dashboard", styles["Section"]))
    story.append(Paragraph(
        "The dashboard is presented as combined sheet-level panels rather than individual chart pages. "
        "Each panel keeps the original chart arrangement together so management can read the dashboard as one analytical view.",
        styles["Normal"],
    ))
    story.append(Spacer(1, 8))

    for sheet_index, sheet in enumerate(sheets or [], start=1):
        panel = _render_dashboard_panel(df, sheet, sheet_index, work_dir)
        if panel:
            story.append(Paragraph(
                f"Dashboard Panel {sheet_index}: {safe(sheet.get('name', 'Dashboard'))}",
                styles["Subsection"],
            ))
            story.append(Image(str(panel), width=174 * mm, height=0.0 * mm))
            # ReportLab needs an explicit height; calculate from image ratio.
            from PIL import Image as _PI
            with _PI.open(panel) as im:
                ratio = im.height / im.width
            # Replace the zero-height flowable with correct dimensions.
            story.pop()
            story.append(Image(str(panel), width=174 * mm, height=174 * mm * ratio))

            chart_titles = [
                safe(c.get("title", "Business view"))
                for c in sorted(sheet.get("charts", []), key=lambda x: x.get("position", 999))
            ]
            desc = safe(sheet.get("description", "Business dashboard analysis."))
            story.append(Paragraph(
                f"<b>Whole-panel explanation:</b> {desc} "
                f"This panel brings together {len(chart_titles)} related views so management can compare the main dimensions and measures together rather than interpreting any single visual in isolation.",
                styles["Small"],
            ))
        if sheet_index != len(sheets or []):
            story.append(PageBreak())

    story.append(PageBreak())

    # --------------------------------------------------------
    # 3. STATISTICS SUMMARY
    # --------------------------------------------------------
    story.append(Paragraph("2. Statistical Analysis — Management Summary", styles["Section"]))
    stat_result = _simple_stat_summary(df)
    if isinstance(stat_result, tuple):
        stat_text, stat_rows = stat_result
    else:
        stat_text, stat_rows = stat_result, []
    story.append(Paragraph(stat_text, styles["Normal"]))
    story.append(Spacer(1, 8))

    if stat_rows:
        table_data = [["Measure", "Average", "Median", "Minimum", "Maximum", "Variation"]]
        for row in stat_rows[:12]:
            table_data.append([
                row["Measure"], fmt_num(row["Average"]), fmt_num(row["Median"]),
                fmt_num(row["Minimum"]), fmt_num(row["Maximum"]), fmt_num(row["Variation"]),
            ])
        add_table(story, table_data, widths=[43 * mm, 25 * mm, 25 * mm, 25 * mm, 25 * mm, 27 * mm], font_size=6.7)

    categorical = df.select_dtypes(include=["object", "category", "bool"])
    story.append(Paragraph("Categorical Pattern Summary", styles["Subsection"]))
    cat_rows = [["Field", "Largest observed group", "Share"]]
    for col in list(categorical.columns)[:8]:
        s = categorical[col].dropna().astype(str)
        if s.empty:
            continue
        vc = s.value_counts()
        cat_rows.append([pretty_column(col), safe(vc.index[0]), f"{vc.iloc[0] / len(s) * 100:.1f}%"])
    if len(cat_rows) > 1:
        add_table(story, cat_rows, widths=[65 * mm, 65 * mm, 40 * mm], font_size=7)
    else:
        story.append(Paragraph("No categorical fields were available for this summary.", styles["Small"]))

    story.append(Paragraph("Statistical Interpretation", styles["Subsection"]))
    story.append(Paragraph(
        "Management should use the statistical results to understand the normal level of each measure, the amount of variation, and whether unusually high or low observations may be influencing averages. "
        "The statistics support decision-making but should be read together with the dashboard and business context.",
        styles["Normal"],
    ))
    story.append(PageBreak())

    # --------------------------------------------------------
    # 4. BUSINESS INSIGHTS
    # --------------------------------------------------------
    story.append(Paragraph("3. Business Insights & Management Focus", styles["Section"]))
    story.append(Paragraph(
        "The following findings are written in plain business language. They describe what the uploaded data shows, why it matters, and what management should focus on next. "
        "No HR interpretation is applied unless the actual dataset supports an HR domain.",
        styles["Normal"],
    ))
    story.append(Spacer(1, 8))

    if hasattr(insights, "iterrows") and not insights.empty:
        sev = insights.get("Severity", pd.Series(dtype=str)).astype(str).str.upper()
        summary = [["Findings", "High Attention", "Medium", "Monitoring"]]
        summary.append([
            str(len(insights)), str(int((sev == "HIGH").sum())),
            str(int((sev == "MEDIUM").sum())), str(int((sev == "LOW").sum()))
        ])
        add_table(story, summary, widths=[42 * mm, 42 * mm, 42 * mm, 42 * mm], font_size=8)

        for _, row in insights.head(8).iterrows():
            area = safe(row.get("Area", "Business Area"))
            problem = safe(row.get("Problem", "Pattern identified."))
            evidence = safe(row.get("Evidence", "Evidence is present in the uploaded data."))
            impact = safe(row.get("Business Impact", "Further review is recommended."))
            story.append(Paragraph(f"<b>{area}</b>", styles["Subsection"]))
            story.append(Paragraph(
                f"<b>What the data shows:</b> {problem}<br/>"
                f"<b>Evidence:</b> {evidence}<br/>"
                f"<b>Why management should care:</b> {impact}<br/>"
                f"<b>Management focus:</b> Validate the pattern against the dashboard, identify the affected segment or measure, and decide what operational action or deeper analysis is required.",
                styles["Normal"],
            ))
            story.append(Spacer(1, 5))
    else:
        story.append(Paragraph("No high-priority business finding was automatically identified from the available fields.", styles["Normal"]))

    story.append(Paragraph("Overall Business Message", styles["Subsection"]))
    story.append(Paragraph(
        "The purpose of this section is not to label the business as good or bad. It identifies where the current data contains concentration, unusual values, outcome imbalance, data-quality limitations, or meaningful relationships that management should investigate.",
        styles["Normal"],
    ))
    story.append(PageBreak())

    # --------------------------------------------------------
    # 5. DOMAIN RESEARCH
    # --------------------------------------------------------
    detailed = research_detail if isinstance(research_detail, dict) else {}
    domain = detailed.get("domain", "")
    if not domain and isinstance(research_result, dict):
        domain = research_result.get("domain", "")
    domain = domain or "General Business Analytics"
    description = detailed.get("dataset_description", "")
    if not description and isinstance(research_result, dict):
        description = research_result.get("analysis", "")

    story.append(Paragraph("4. Domain Research — Simple Business Explanation", styles["Section"]))
    story.append(Paragraph(f"<b>Detected domain:</b> {safe(domain)}", styles["Normal"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        safe(description or "The dataset has been interpreted from its actual columns and available research evidence."),
        styles["Normal"],
    ))

    story.append(Paragraph("What this dataset can support", styles["Subsection"]))
    uses = detailed.get("business_uses", [])
    if uses:
        for use in uses[:8]:
            story.append(Paragraph(f"• {safe(use)}", styles["Small"]))
    else:
        story.append(Paragraph("Business performance monitoring, segmentation, trend analysis and decision support based on the available fields.", styles["Small"]))

    story.append(Paragraph("Key Variables", styles["Subsection"]))
    numeric_cols = list(df.select_dtypes(include="number").columns)
    cat_cols = list(df.select_dtypes(include=["object", "category", "bool"]).columns)
    key_data = [["Business measure candidates", "Business grouping candidates"]]
    for i in range(max(len(numeric_cols), len(cat_cols), 1)):
        if i >= 12:
            break
        key_data.append([
            pretty_column(numeric_cols[i]) if i < len(numeric_cols) else "",
            pretty_column(cat_cols[i]) if i < len(cat_cols) else "",
        ])
    add_table(story, key_data, widths=[85 * mm, 85 * mm], font_size=7)

    story.append(Paragraph("Column-by-Column Explanation", styles["Subsection"]))
    column_rows = detailed.get("column_rows", [])
    if column_rows:
        col_data = [["Column", "Type", "Simple meaning", "Missing"]]
        for item in column_rows[:16]:
            if not isinstance(item, dict):
                continue
            col_data.append([
                pretty_column(item.get("Column", "")),
                safe(item.get("Data Type", "")),
                safe(item.get("Meaning / Explanation", "Available field used for analysis.")),
                safe(item.get("Missing Values", 0)),
            ])
        add_table(story, col_data, widths=[37 * mm, 27 * mm, 88 * mm, 18 * mm], font_size=6.7)
        if len(column_rows) > 16:
            story.append(Paragraph(
                f"The dataset contains {len(column_rows):,} documented fields. The table above highlights the first 16 to keep the management report concise.",
                styles["Small"],
            ))

    evidence = detailed.get("online_evidence", [])
    if evidence:
        story.append(Paragraph("Research Evidence", styles["Subsection"]))
        for item in evidence[:4]:
            story.append(Paragraph(f"• {safe(item)}", styles["Small"]))
    story.append(PageBreak())

    # --------------------------------------------------------
    # 6. MANAGEMENT QUESTIONS — ALL QUESTIONS + EXPLANATIONS
    # --------------------------------------------------------
    story.append(Paragraph("5. Management Focus Questions", styles["Section"]))
    story.append(Paragraph(
        "These are the business questions generated from the uploaded schema. Each question is included because it represents an area management can investigate using the dashboard and available data. The explanation below each question describes why the area deserves attention.",
        styles["Normal"],
    ))
    story.append(Spacer(1, 8))

    all_questions = []
    seen = set()
    for q in (questions or []):
        q = re.sub(r"\s+", " ", str(q)).strip()
        if q and q.lower() not in seen:
            seen.add(q.lower())
            all_questions.append(q)

    if all_questions:
        for i, q in enumerate(all_questions, start=1):
            story.append(Paragraph(f"<b>{i}. {safe(q)}</b>", styles["Question"]))
            story.append(Paragraph(
                f"<b>Why management should focus on this:</b> {_management_explanation(df, q)}",
                styles["Small"],
            ))
            story.append(Spacer(1, 5))
    else:
        story.append(Paragraph("No business questions were generated for this dataset.", styles["Normal"]))
    story.append(PageBreak())

    # --------------------------------------------------------
    # 7. RECOMMENDATIONS + DEVELOPMENT OPPORTUNITIES
    # --------------------------------------------------------
    story.append(Paragraph("6. Recommendations & Development Opportunities", styles["Section"]))
    story.append(Paragraph(
        "Recommendations below are connected to the observed dataset structure and findings. They are written as practical next steps rather than generic industry advice.",
        styles["Normal"],
    ))
    story.append(Spacer(1, 8))

    recs = recommendations or []
    if recs:
        for i, item in enumerate(recs[:10], start=1):
            if isinstance(item, dict):
                title = item.get("Problem") or item.get("Title") or item.get("Recommendation") or f"Recommendation {i}"
                action = item.get("What business should do") or item.get("Action") or item.get("Recommendation") or "Review the relevant dataset pattern and define a measurable action."
                help_text = item.get("How this helps") or item.get("Business Impact") or item.get("Impact") or "Creates a clearer basis for management follow-up."
            else:
                title = f"Recommendation {i}"
                action = str(item)
                help_text = "Use the dashboard evidence to validate the action before implementation."
            story.append(Paragraph(f"<b>{i}. {safe(title)}</b>", styles["Subsection"]))
            story.append(Paragraph(
                f"<b>What to do:</b> {safe(action)}<br/><b>How it helps:</b> {safe(help_text)}",
                styles["Normal"],
            ))

    story.append(Paragraph("Development Opportunities", styles["Subsection"]))
    dev = [
        "Automate recurring data-quality checks before each dashboard refresh.",
        "Add segment-level monitoring for the business dimensions identified as important in the dashboard.",
        "Track the management questions as measurable KPIs so future reports can compare changes over time.",
        "Use the strongest relationships and outcome fields as candidates for predictive or scenario analysis where appropriate.",
    ]
    for item in dev:
        story.append(Paragraph(f"• {item}", styles["Small"]))

    if user_analysis:
        story.append(Paragraph("User-Requested AI Analysis", styles["Subsection"]))
        story.append(Paragraph(safe(user_analysis), styles["Small"]))
    story.append(PageBreak())

    # --------------------------------------------------------
    # 8. DATA QUALITY + FINAL MANAGEMENT TAKEAWAY
    # --------------------------------------------------------
    story.append(Paragraph("7. Data Quality & Final Management Takeaway", styles["Section"]))
    quality_data = [
        ["Quality Check", "Result", "Management meaning"],
        ["Records", f"{len(df):,}", "Available observations in the uploaded file."],
        ["Columns", f"{len(df.columns):,}", "Available measures and business dimensions."],
        ["Missing cells", f"{missing_total:,}", "Review affected fields before using them for critical decisions."],
        ["Duplicate rows", f"{duplicate_total:,}", "Confirm whether repeated rows are genuine or accidental."],
        ["Data quality indicator", f"{quality}%", "Simple completeness-based indicator; not a full validation score."],
    ]
    add_table(story, quality_data, widths=[45 * mm, 35 * mm, 90 * mm], font_size=7.2)

    story.append(Paragraph("Final Management Takeaway", styles["Subsection"]))
    story.append(Paragraph(
        "Use the dashboard as the visual starting point, the statistical summary to understand scale and variation, the business insights to identify where attention is needed, and the management questions to guide the next investigation. "
        "The report is evidence-based and should be combined with operational knowledge before any major business decision is made.",
        styles["Normal"],
    ))

    if dashboard_url:
        href = escape(str(dashboard_url), quote=True)
        story.append(Spacer(1, 18))
        story.append(Paragraph("Interactive Dashboard", styles["Subsection"]))
        story.append(Paragraph(
            f'<link href="{href}"><u>🔗 OPEN INTERACTIVE DASHBOARD PAGE</u></link>',
            styles["Link"],
        ))
        story.append(Paragraph(
            f"Dashboard page: {safe(dashboard_url)}",
            styles["Small"],
        ))

    document.build(story, onFirstPage=_footer, onLaterPages=_footer)
