from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import os

class PDFExporter:
    @staticmethod
    def generate_report(data, sld_pixmap, filename="ELECDRAFT_Project_Report.pdf"):
        doc = SimpleDocTemplate(filename, pagesize=landscape(letter))
        elements = []
        styles = getSampleStyleSheet()

        # Title
        elements.append(Paragraph("<b>ELECDRAFT: PROFESSIONAL ELECTRICAL DESIGN REPORT</b>", styles['Title']))
        elements.append(Spacer(1, 12))

        # 1. Load Schedule Table
        elements.append(Paragraph("<b>I. Automated Load Schedule (PEC 2017)</b>", styles['Heading2']))
        table_data = [["Description", "Load (VA)", "Amps (I)", "Breaker", "Wire Size", "V-Drop"]]
        for row in data:
            table_data.append([row['name'], str(row['va']), f"{row['amps']}A", f"{row['breaker']}A", row['wire'], f"{row['v_drop']}%"])

        t = Table(table_data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2c3e50")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
        ]))
        elements.append(t)
        elements.append(Spacer(1, 20))

        # 2. SLD Snapshot
        # Note: You must save the SLD pixmap to a temporary file first
        elements.append(Paragraph("<b>II. Single-Line Diagram Schematic</b>", styles['Heading2']))
        temp_img = "temp_sld.png"
        sld_pixmap.save(temp_img)
        img = Image(temp_img, width=400, height=300)
        elements.append(img)

        doc.build(elements)
        if os.path.exists(temp_img):
            os.remove(temp_img)
        return filename