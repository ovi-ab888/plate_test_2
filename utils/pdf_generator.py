# utils/pdf_generator.py

"""
PDF Report Generator - With Larger Font Sizes
"""

from io import BytesIO
from datetime import datetime
from typing import Dict, List, Any

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.units import inch
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


def generate_pdf_report(plates: List[Dict[str, Any]], demand: Dict[str, int],
                        original_qty: Dict[str, int], algo_name: str,
                        waste_percent: float, styles_dict: Dict[str, str] = None,
                        colors_dict: Dict[str, str] = None,
                        sizes_dict: Dict[str, str] = None,
                        job_number: str = "") -> BytesIO:
    """Generate professional PDF report with larger fonts"""
    
    if not REPORTLAB_AVAILABLE:
        return None
    
    if styles_dict is None:
        styles_dict = {}
    if colors_dict is None:
        colors_dict = {}
    if sizes_dict is None:
        sizes_dict = {}
    
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=landscape(A4),
            rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30
        )
        styles = getSampleStyleSheet()
        
        # ================================================================
        # CUSTOM STYLES WITH LARGER FONTS
        # ================================================================
        
        # Title - বড় ফন্ট
        title_style = ParagraphStyle(
            'CustomTitle', parent=styles['Heading1'],
            fontSize=18, alignment=TA_CENTER,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        
        # Job Number - মাঝারি ফন্ট
        job_style = ParagraphStyle(
            'JobStyle', parent=styles['Heading2'],
            fontSize=14, alignment=TA_CENTER,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        
        # Subtitle - মাঝারি ফন্ট
        subtitle_style = ParagraphStyle(
            'CustomSubtitle', parent=styles['Normal'],
            fontSize=11, alignment=TA_CENTER,
            textColor=colors.grey,
            spaceAfter=14,
            fontName='Helvetica'
        )
        
        # Section Header - বড় ফন্ট
        section_header_style = ParagraphStyle(
            'SectionHeader', parent=styles['Heading2'],
            fontSize=15, alignment=TA_CENTER,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        # Table Header - বড় ফন্ট
        table_header_style = ParagraphStyle(
            'TableHeader', parent=styles['Normal'],
            fontSize=10, alignment=TA_CENTER,
            textColor=colors.white,
            fontName='Helvetica-Bold'
        )
        
        # Table Cell - বড় ফন্ট
        table_cell_style = ParagraphStyle(
            'TableCell', parent=styles['Normal'],
            fontSize=9, alignment=TA_CENTER,
            fontName='Helvetica'
        )
        
        # Table Cell Bold - বড় ফন্ট
        table_cell_bold_style = ParagraphStyle(
            'TableCellBold', parent=styles['Normal'],
            fontSize=10, alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        # Footer - ছোট ফন্ট
        footer_style = ParagraphStyle(
            'Footer', parent=styles['Normal'],
            fontSize=9, alignment=TA_CENTER,
            textColor=colors.grey,
            spaceTop=14,
            fontName='Helvetica'
        )
        
        story = []
        
        # ================================================================
        # HEADER
        # ================================================================
        story.append(Paragraph("📊 Plate Ratio System - Report", title_style))
        if job_number:
            story.append(Paragraph(f"🔢 Job Number: {job_number}", job_style))
        story.append(Paragraph(
            f"Algorithm: {algo_name} | Waste: {waste_percent}% | "
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            subtitle_style
        ))
        story.append(Spacer(1, 12))
        
        # ================================================================
        # MAIN SUMMARY TABLE
        # ================================================================
        
        # Build header with all columns
        header_row = ["SL", "Tag", "Original", "With Add-on"]
        for p in plates:
            header_row.append(f"Plate {p['name']}")
        header_row.extend(["Total Prod.", "Excess", "Excess %"])
        
        summary_data = [header_row]
        
        # Build data rows
        sl = 1
        for tag in demand.keys():
            style = styles_dict.get(tag, "")
            color = colors_dict.get(tag, "")
            size = sizes_dict.get(tag, "")
            
            # Tag with style info
            tag_display = tag
            if style:
                tag_display = f"{tag}"
            
            row = [str(sl), tag_display, 
                   str(original_qty.get(tag, 0)), str(demand[tag])]
            
            total_produced = 0
            for p in plates:
                ups = p["layout"].get(tag, 0)
                row.append(str(ups))
                total_produced += ups * p["sheets"]
            
            excess = total_produced - demand[tag]
            excess_percent = f"{round((excess / demand[tag]) * 100, 2) if demand[tag] else 0}%"
            row.extend([str(total_produced), str(excess), excess_percent])
            summary_data.append(row)
            sl += 1
        
        # Total row
        total_row = ["📊", "TOTAL", "", 
                     str(sum(original_qty.values())), str(sum(demand.values()))]
        
        total_produced_sum = 0
        for p in plates:
            plate_total = 0
            for tag in demand:
                plate_total += p["layout"].get(tag, 0) * p["sheets"]
            total_row.append(str(plate_total))
            total_produced_sum += plate_total
        
        total_excess_sum = total_produced_sum - sum(demand.values())
        total_excess_percent = (
            f"{round((total_excess_sum / total_produced_sum) * 100, 2) if total_produced_sum > 0 else 0}%"
        )
        total_row.extend([str(total_produced_sum), str(total_excess_sum), total_excess_percent])
        summary_data.append(total_row)
        
        # Create main table
        main_table = Table(summary_data, repeatRows=1)
        
        # Table style with larger fonts
        table_style = [
            # Header row - বড় ফন্ট, গাঢ়
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),  # Header font size বড়
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            
            # Data rows - বড় ফন্ট
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),  # Data font size বড়
            ('ALIGN', (0, 1), (-1, -2), 'CENTER'),
            ('VALIGN', (0, 1), (-1, -2), 'MIDDLE'),
            
            # Total row - বড় ফন্ট, গাঢ়
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 10),  # Total row font size বড়
            ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, -1), (-1, -1), 'MIDDLE'),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.8, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]
        
        # Alternating row colors
        for i in range(1, len(summary_data) - 1):
            if i % 2 == 0:
                table_style.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8f9fa')))
        
        main_table.setStyle(TableStyle(table_style))
        story.append(main_table)
        story.append(Spacer(1, 18))
        
        # ================================================================
        # PLATE DETAILS TABLE
        # ================================================================
        story.append(Paragraph("🧾 Plate Configuration Details", section_header_style))
        story.append(Spacer(1, 10))
        
        plate_data = [["SL", "Plate ID", "Sheets", "Total UPS", "Layout"]]
        
        for idx, p in enumerate(plates, 1):
            layout_str = ", ".join([f"{k}:{v}" for k, v in p["layout"].items()])
            plate_data.append([
                str(idx),
                p["name"],
                str(p["sheets"]),
                str(sum(p["layout"].values())),
                layout_str
            ])
        
        # Add total row for plate details
        total_sheets = sum(p["sheets"] for p in plates)
        total_ups = sum(sum(p["layout"].values()) for p in plates)
        plate_data.append([
            "📊",
            "TOTAL",
            str(total_sheets),
            str(total_ups),
            "-"
        ])
        
        plate_table = Table(plate_data)
        plate_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('VALIGN', (0, 0), (-1, 0), 'MIDDLE'),
            
            # Data rows
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 9),
            ('ALIGN', (0, 1), (-1, -2), 'CENTER'),
            ('VALIGN', (0, 1), (-1, -2), 'MIDDLE'),
            
            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#f0f0f0')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 10),
            ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
            ('VALIGN', (0, -1), (-1, -1), 'MIDDLE'),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 0.8, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Padding
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        
        story.append(plate_table)
        story.append(Spacer(1, 18))
        
        # ================================================================
        # FOOTER
        # ================================================================
        story.append(Paragraph(
            f"Report Generated by Plate Ratio System | Job: {job_number if job_number else 'N/A'} | Design by Ovi | All Rights Reserved",
            footer_style
        ))
        
        # Build the PDF
        doc.build(story)
        buffer.seek(0)
        return buffer

    except Exception as e:
        print(f"PDF Generation Error: {str(e)}")
        return None
