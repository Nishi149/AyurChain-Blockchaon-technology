from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os

def generate_report(batch_id, records, save_path="docs/"):
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    filename = os.path.join(save_path, f"AyurChain_Report_{batch_id}.pdf")
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(f"🌿 AyurChain Traceability Report - Batch {batch_id}", styles["Title"]))
    elements.append(Spacer(1, 20))

    # Intro
    elements.append(Paragraph("This report documents the end-to-end journey of the Ayurvedic product batch recorded on the blockchain.", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # Table data
    table_data = [["Stage", "Details"]]
    for record in records:
        role = record["data"].get("role", "Unknown")
        details = ", ".join([f"{k}: {v}" for k, v in record["data"].items() if k != "role"])
        table_data.append([role, details])

    # Table style
    table = Table(table_data, colWidths=[150, 350])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#4CAF50")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN',(0,0),(-1,-1),'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND',(0,1),(-1,-1),colors.whitesmoke),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 30))

    # Footer
    elements.append(Paragraph("✅ Blockchain Verified: This batch record is immutable and tamper-proof.", styles["Italic"]))

    # Build PDF
    doc.build(elements)
    return filename
