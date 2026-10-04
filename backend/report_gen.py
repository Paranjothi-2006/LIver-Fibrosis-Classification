import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

def generate_pdf_report(patient_info, prediction, confidence, heatmap_path, output_pdf_path="clinical_report.pdf"):
    doc = SimpleDocTemplate(output_pdf_path, pagesize=letter, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    styles = getSampleStyleSheet()

    # Custom Heading & Paragraph Styles
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=18, textColor=colors.HexColor("#1A3650"))
    heading_style = ParagraphStyle('HeadingStyle', parent=styles['Heading2'], fontSize=12, textColor=colors.HexColor("#286090"))
    normal_style = ParagraphStyle('NormalStyle', parent=styles['Normal'], fontSize=10, leading=14, textColor=colors.HexColor("#2D3748"))

    # Title
    story.append(Paragraph("<b>CLINICAL LIVER FIBROSIS ASSESSMENT REPORT</b>", title_style))
    story.append(Spacer(1, 10))

    # Patient Details Table
    patient_data = [
        [Paragraph("<b>Patient Name:</b>", normal_style), Paragraph(patient_info.get('name', 'N/A'), normal_style),
         Paragraph("<b>Patient ID:</b>", normal_style), Paragraph(patient_info.get('id', 'N/A'), normal_style)],
        [Paragraph("<b>Age / Gender:</b>", normal_style), Paragraph(f"{patient_info.get('age', 'N/A')} / {patient_info.get('gender', 'N/A')}", normal_style),
         Paragraph("<b>Date:</b>", normal_style), Paragraph(patient_info.get('date', 'N/A'), normal_style)]
    ]
    t_patient = Table(patient_data, colWidths=[100, 160, 80, 160])
    t_patient.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EDF2F7")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_patient)
    story.append(Spacer(1, 15))

    # Diagnostic Summary Table
    story.append(Paragraph("<b>Diagnostic Prediction Summary</b>", heading_style))
    stage_info = {
        'F0': "F0: No Fibrosis - Normal liver parenchyma.",
        'F1': "F1: Mild Fibrosis - Portal fibrosis without septa.",
        'F2': "F2: Moderate Fibrosis - Portal fibrosis with few septa.",
        'F3': "F3: Severe Fibrosis - Numerous septa without cirrhosis.",
        'F4': "F4: Cirrhosis - Advanced scarring and nodular liver structures."
    }
    
    clean_stage = prediction.split()[0] if ' ' in prediction else prediction

    diag_data = [
        [Paragraph("<b>Predicted Fibrosis Stage:</b>", normal_style), Paragraph(f"<b>{prediction}</b>", normal_style)],
        [Paragraph("<b>Confidence Score:</b>", normal_style), Paragraph(f"{confidence:.2f}%", normal_style)],
        [Paragraph("<b>Clinical Description:</b>", normal_style), Paragraph(stage_info.get(clean_stage, "N/A"), normal_style)]
    ]
    t_diag = Table(diag_data, colWidths=[150, 350])
    t_diag.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#EBF8FF")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#BEE3F8")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_diag)
    story.append(Spacer(1, 15))

    # Explainable AI (Grad-CAM) Visual
    story.append(Paragraph("<b>Explainable AI (Grad-CAM) Visual Localization</b>", heading_style))
    if os.path.exists(heatmap_path):
        img = Image(heatmap_path, width=400, height=200)
        story.append(img)
        story.append(Spacer(1, 10))

    # Disclaimer
    disclaimer_text = "<i>Note: This AI-generated assessment is intended as a clinical decision-support tool and must be verified by a certified Radiologist or Hepatologist.</i>"
    story.append(Paragraph(disclaimer_text, ParagraphStyle('Disc', parent=styles['Italic'], fontSize=8, textColor=colors.gray)))

    doc.build(story)
    return output_pdf_path