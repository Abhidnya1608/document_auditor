#converts Audit report to exportable PDF

from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from src.agent.schemas import AuditReport


def generate_pdf_report(report: AuditReport, output_path: str | Path) -> Path:
    """Generates a styled PDF report summarizing audit findings."""
    doc = SimpleDocTemplate(str(output_path), pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom typography styles
    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontSize=20,
        leading=24,
        textColor=colors.HexColor("#1E3A8A"),
        spaceAfter=12,
    )
    meta_style = ParagraphStyle(
        "DocMeta",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor("#4B5563"),
        spaceAfter=18,
    )
    cell_style = ParagraphStyle(
        "CellText",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
    )
    bold_cell_style = ParagraphStyle(
        "BoldCellText",
        parent=styles["Normal"],
        fontSize=9,
        leading=12,
        fontName="Helvetica-Bold",
    )

    story = []

    # Title & Metadata Header
    story.append(Paragraph("🛡️ Document Audit Compliance Report", title_style))
    story.append(
        Paragraph(
            f"<b>Audited Document:</b> {report.document_name} | "
            f"<b>Total Rules Evaluated:</b> {report.total_rules_checked}",
            meta_style,
        )
    )
    story.append(Spacer(1, 10))

    # Table Setup
    table_data = [
        [
            Paragraph("Rule / Requirement", bold_cell_style),
            Paragraph("Status", bold_cell_style),
            Paragraph("Page", bold_cell_style),
            Paragraph("Evidence Quote", bold_cell_style),
        ]
    ]

    for finding in report.findings:
        # Style status text color
        status_color = "#16A34A" if finding.status == "PASS" else ("#DC2626" if finding.status == "FAIL" else "#D97706")
        status_p = Paragraph(f"<font color='{status_color}'><b>{finding.status}</b></font>", cell_style)

        rule_p = Paragraph(finding.rule, cell_style)
        page_p = Paragraph(str(finding.page_number), cell_style)
        evidence_p = Paragraph(f"<i>\"{finding.evidence}\"</i>", cell_style)

        table_data.append([rule_p, status_p, page_p, evidence_p])

    col_widths = [160, 65, 40, 275]
    report_table = Table(table_data, colWidths=col_widths)

    report_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#F3F4F6")),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E5E7EB")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("TOPPADDING", (0, 1), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
            ]
        )
    )

    story.append(report_table)
    doc.build(story)
    return Path(output_path)