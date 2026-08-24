"""
Reporting service — PDF forensic report generation using ReportLab.
"""

import os
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


REPORTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "reports")


def ensure_reports_dir():
    """Ensure the reports directory exists."""
    os.makedirs(REPORTS_DIR, exist_ok=True)


def generate_forensic_report(
    case_data: dict,
    evidence_list: list,
    recovery_jobs: list,
    custody_events: list,
    integrity_records: list,
    investigator_name: str = "System",
) -> str:
    """
    Generate a comprehensive PDF forensic investigation report.
    Returns the file path of the generated PDF.
    """
    ensure_reports_dir()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    case_num = case_data.get("case_number", "UNKNOWN")
    filename = f"ForensicReport_{case_num}_{timestamp}.pdf"
    filepath = os.path.join(REPORTS_DIR, filename)

    doc = SimpleDocTemplate(
        filepath,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=25 * mm,
        bottomMargin=25 * mm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=22,
        spaceAfter=6,
        textColor=colors.HexColor("#1E293B"),
        fontName="Helvetica-Bold",
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=11,
        spaceAfter=20,
        textColor=colors.HexColor("#64748B"),
        alignment=TA_CENTER,
    )

    heading_style = ParagraphStyle(
        "SectionHeading",
        parent=styles["Heading2"],
        fontSize=14,
        spaceBefore=16,
        spaceAfter=8,
        textColor=colors.HexColor("#1E293B"),
        fontName="Helvetica-Bold",
        borderWidth=0,
        borderPadding=0,
    )

    body_style = ParagraphStyle(
        "BodyText",
        parent=styles["Normal"],
        fontSize=10,
        spaceAfter=4,
        textColor=colors.HexColor("#334155"),
    )

    label_style = ParagraphStyle(
        "FieldLabel",
        parent=styles["Normal"],
        fontSize=9,
        textColor=colors.HexColor("#64748B"),
        fontName="Helvetica-Bold",
    )

    elements = []

    # ===== HEADER =====
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("FORENSIC INVESTIGATION REPORT", title_style))
    elements.append(Paragraph("ForensicRecover — Digital Evidence Recovery & Verification Platform", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#4F46E5")))
    elements.append(Spacer(1, 12))

    # ===== CASE INFORMATION =====
    elements.append(Paragraph("1. CASE INFORMATION", heading_style))

    case_table_data = [
        ["Case Number", case_data.get("case_number", "N/A")],
        ["Case Type", case_data.get("case_type", "N/A")],
        ["Description", case_data.get("description", "N/A")],
        ["Status", case_data.get("status", "N/A")],
        ["Created", case_data.get("created_at", "N/A")],
        ["Investigator", investigator_name],
    ]

    case_table = Table(case_table_data, colWidths=[150, 350])
    case_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F1F5F9")),
        ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#475569")),
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(case_table)
    elements.append(Spacer(1, 12))

    # ===== EVIDENCE INFORMATION =====
    elements.append(Paragraph("2. EVIDENCE INFORMATION", heading_style))

    for ev in evidence_list:
        ev_data = [
            ["Evidence ID", ev.get("evidence_id", "N/A")],
            ["Device Type", ev.get("device_type", "N/A")],
            ["Manufacturer", ev.get("manufacturer", "N/A")],
            ["Model", ev.get("model", "N/A")],
            ["Serial Number", ev.get("serial_number", "N/A")],
            ["Capacity", ev.get("capacity", "N/A")],
            ["Filesystem", ev.get("filesystem", "N/A")],
            ["Status", ev.get("status", "N/A")],
        ]
        ev_table = Table(ev_data, colWidths=[150, 350])
        ev_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F1F5F9")),
            ("TEXTCOLOR", (0, 0), (0, -1), colors.HexColor("#475569")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(ev_table)
        elements.append(Spacer(1, 8))

    # ===== RECOVERY RESULTS =====
    elements.append(Paragraph("3. RECOVERY RESULTS", heading_style))

    for job in recovery_jobs:
        job_data = job.get("job", job)
        elements.append(Paragraph(f"Recovery Job #{job_data.get('id', 'N/A')}", body_style))

        recovery_summary = [
            ["Files Found", str(job_data.get("files_found", 0))],
            ["Fully Recovered", str(job_data.get("files_recovered", 0))],
            ["Partially Recovered", str(job_data.get("files_partial", 0))],
            ["Failed / Not Recoverable", str(job_data.get("files_failed", 0))],
            ["Status", job_data.get("status", "N/A")],
            ["Started", job_data.get("started_at", "N/A")],
            ["Completed", job_data.get("completed_at", "N/A")],
        ]

        rec_table = Table(recovery_summary, colWidths=[180, 320])
        rec_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#F1F5F9")),
            ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ]))
        elements.append(rec_table)
        elements.append(Spacer(1, 6))

        # Artifacts table
        artifacts = job.get("artifacts", [])
        if artifacts:
            elements.append(Paragraph("Recovered Artifacts:", body_style))
            art_header = ["#", "Filename", "Type", "Status", "Size"]
            art_rows = [art_header]
            for i, art in enumerate(artifacts, 1):
                size_val = art.get("size", 0)
                if size_val and size_val > 1048576:
                    size_str = f"{size_val / 1048576:.1f} MB"
                elif size_val and size_val > 1024:
                    size_str = f"{size_val / 1024:.1f} KB"
                else:
                    size_str = f"{size_val} B" if size_val else "N/A"

                art_rows.append([
                    str(i),
                    art.get("original_name", "N/A")[:30],
                    art.get("artifact_type", "N/A"),
                    art.get("recovery_status", "N/A"),
                    size_str,
                ])

            art_table = Table(art_rows, colWidths=[30, 150, 80, 130, 80])
            art_table.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ]))
            elements.append(art_table)
            elements.append(Spacer(1, 12))

    # ===== CHAIN OF CUSTODY =====
    elements.append(Paragraph("4. CHAIN OF CUSTODY", heading_style))

    if custody_events:
        cust_header = ["#", "Action", "From", "To", "Time", "Remarks"]
        cust_rows = [cust_header]
        for i, evt in enumerate(custody_events, 1):
            cust_rows.append([
                str(i),
                evt.get("action", "N/A"),
                evt.get("from_user", "N/A") or "—",
                evt.get("to_user", "N/A") or "—",
                str(evt.get("timestamp", "N/A"))[:19],
                (evt.get("remarks", "") or "—")[:40],
            ])

        cust_table = Table(cust_rows, colWidths=[25, 100, 70, 70, 110, 110])
        cust_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ]))
        elements.append(cust_table)
    else:
        elements.append(Paragraph("No custody events recorded.", body_style))

    elements.append(Spacer(1, 12))

    # ===== INTEGRITY VERIFICATION =====
    elements.append(Paragraph("5. INTEGRITY VERIFICATION", heading_style))

    if integrity_records:
        for rec in integrity_records:
            elements.append(Paragraph(
                f"Algorithm: {rec.get('algorithm', 'SHA-256')} | "
                f"Hash: {rec.get('hash_value', 'N/A')[:32]}... | "
                f"Purpose: {rec.get('purpose', 'N/A')}",
                body_style
            ))
    else:
        elements.append(Paragraph("No integrity records available.", body_style))

    elements.append(Spacer(1, 20))

    # ===== FOOTER =====
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#CBD5E1")))
    elements.append(Spacer(1, 8))

    footer_style = ParagraphStyle(
        "Footer", parent=styles["Normal"], fontSize=8,
        textColor=colors.HexColor("#94A3B8"), alignment=TA_CENTER,
    )
    elements.append(Paragraph(
        f"Generated by ForensicRecover | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"Investigator: {investigator_name}",
        footer_style,
    ))
    elements.append(Paragraph(
        "This report is generated for authorized investigation purposes only.",
        footer_style,
    ))

    doc.build(elements)
    return filepath
