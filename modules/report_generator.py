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

    document.build(story)
