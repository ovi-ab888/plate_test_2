"""
Plate Ratio System - Complete Edition V1-V26
With Password Authentication, Modern UI & Report Download
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import math
from math import ceil

# Import from algorithms
from algorithms import ALGORITHM_REGISTRY, get_algorithm
from algorithms.v1_helpers import calculate_waste_percent, build_full_summary

# ================================================================
# STREAMLIT PAGE CONFIGURATION
# ================================================================
st.set_page_config(
    page_title="Plate Ratio System - Complete Edition",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================================================
# PASSWORD AUTHENTICATION (MULTIPLE PASSWORDS SUPPORT)
# ================================================================
def check_password():
    expected_passwords = None
    try:
        # It can be a list of passwords in secrets.toml: app_passwords = ["pass1", "pass2"]
        expected_passwords = st.secrets.get("app_passwords", None)
        if expected_passwords is None:
            # Fallback to single password secret if app_passwords isn't found
            single_pass = st.secrets.get("app_password", None)
            if single_pass:
                expected_passwords = [single_pass]
    except Exception:
        pass
    
    # Fallback to Environment Variable
    if expected_passwords is None:
        env_pass = os.environ.get("PEPCO_APP_PASSWORD")
        if env_pass:
            expected_passwords = [env_pass]
    
    if expected_passwords is None:
        st.error("App passwords not configured. Please set 'app_passwords' in secrets or PEPCO_APP_PASSWORD environment variable.")
        return False

    # Ensure it's a list or set for membership testing
    if isinstance(expected_passwords, str):
        expected_passwords = [expected_passwords]

    def _password_entered():
        entered_pass = st.session_state.get("password", "")
        if entered_pass in expected_passwords:
            st.session_state["password_correct"] = True
            try:
                del st.session_state["password"]
            except Exception:
                pass
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", None) is True:
        return True

    # Password Page Styling
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        * { font-family: 'Inter', sans-serif; }
        .stApp {
            background: linear-gradient(-45deg, #0f0c29, #1a1a3e, #24243e, #1a1a3e);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
        }
        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        .main > div { background: transparent !important; padding: 0 !important; }
        .block-container { padding: 0rem !important; max-width: 90% !important; }
        .main-header {
            background: linear-gradient(135deg, rgba(102,126,234,0.15) 0%, rgba(118,75,162,0.15) 100%);
            backdrop-filter: blur(10px);
            padding: 2rem;
            border-radius: 30px;
            margin: 1rem 1rem 0rem 1rem;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
        }
        .main-header h1 {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 800;
            margin: 0;
        }
        .password-container {
            max-width: 460px;
            margin: 40px auto 8px auto;
            padding: 2.8rem 2rem 1.8rem 2rem;
            background: rgba(255,255,255,0.05);
            backdrop-filter: blur(20px);
            border-radius: 32px;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.1);
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.3);
        }
        .lock-icon { font-size: 3rem; margin: 1rem 0; animation: bounce 2s infinite; }
        @keyframes bounce { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-10px); } }
        .stTextInput { margin-top: -10px !important; }
        .stTextInput input {
            background: rgba(255,255,255,0.08) !important;
            border: 1px solid rgba(255,255,255,0.2) !important;
            border-radius: 30px !important;
            color: white !important;
            text-align: center !important;
            font-size: 1.1rem !important;
            padding: 0.9rem 1.5rem !important;
            letter-spacing: 3px;
        }
        #MainMenu, header, footer {visibility: hidden;}
        .designer-name {
            color: rgba(255,255,255,0.6) !important;
            font-size: 0.85rem !important;
            margin-top: 0.5rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="main-header">
        <h1>📊 Plate Ratio System</h1>
        <p>Intelligent Production Planning & Ratio Optimization</p>
        <p style="font-size: 0.85rem; opacity: 0.8;">AI-Powered • Fast • Accurate</p>
        <p class="designer-name">✨ Design by Ovi ✨</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="password-container">
        <h2 style="color: white; margin: 0;">Welcome Back</h2>
        <div class="lock-icon">🔐</div>
        <p style="color: rgba(255,255,255,0.7);">Enter your secure access code to continue</p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1.4, 1.1, 1.4])
    with col2:
        st.text_input(
            label="",
            type="password",
            key="password",
            on_change=_password_entered,
            label_visibility="collapsed",
            placeholder="••••••••"
        )

    if st.session_state.get("password_correct") is False:
        st.error("❌ Your password is incorrect. Please contact Mr. Ovi")

    return False

# ================================================================
# LOAD CUSTOM CSS
# ================================================================
def load_css():
    try:
        with open("static/css/style.css", "r") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        # Fallback CSS if file not found
        st.markdown("""
        <style>
            .main-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem;
                border-radius: 20px;
                text-align: center;
                margin-bottom: 2rem;
            }
            .main-header h1 {
                color: white;
                font-size: 2.5rem;
                font-weight: 700;
                margin: 0;
            }
            .main-header p {
                color: rgba(255,255,255,0.9);
                margin: 0.5rem 0;
            }
            .best-algo {
                background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
                padding: 1.5rem;
                border-radius: 20px;
                text-align: center;
                color: white;
                margin: 1rem 0;
            }
        </style>
        """, unsafe_allow_html=True)

# ================== APP START ==================
if not check_password():
    st.stop()

# Load CSS
load_css()

# ================================================================
# SIDEBAR - শুধু Input Method
# ================================================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; padding: 0.5rem 0 1rem 0;">
        <h3 style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;">📦 Input Method</h3>
    </div>
    """, unsafe_allow_html=True)
    
    input_method = st.radio(
        "Select Input Method:",
        ["✏️ Manual Entry", "📂 Upload Excel"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("---")
    
    # Algorithm Info
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%); border-radius: 10px; padding: 0.75rem; text-align: center; border: 1px solid rgba(102,126,234,0.2);">
        <p style="margin: 0; font-size: 0.75rem; color: rgba(255,255,255,0.5);">🧠 {len(ALGORITHM_REGISTRY)} Algorithms</p>
        <p style="margin: 0; font-size: 0.65rem; color: rgba(255,255,255,0.3);">V1 - V26 Complete</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # About
    with st.expander("📊 About", expanded=False):
        st.markdown("""
        **26 Algorithms:**
        - V1-V10: Classical
        - V11-V18: Evolutionary
        - V19-V26: AI & ML
        
        **Features:**
        - Excel & PDF Reports
        - Dark/Light Mode
        - Production Ready
        """)

# ================================================================
# MAIN UI - Header
# ================================================================
st.markdown("""
<div class="main-header">
    <h1>📊 Plate Ratio Intelligence System</h1>
    <p>Complete Edition • 26 Algorithms • Production Ready</p>
    <p style="font-size: 0.85rem; opacity: 0.8;">AI-Powered • Fast • Accurate</p>
    <p style="color: rgba(255,255,255,0.6); font-size: 0.85rem;">✨ Design by Ovi ✨</p>
</div>
""", unsafe_allow_html=True)

# ================================================================
# MAIN CONTENT - Configuration (৫ কলাম)
# ================================================================
st.markdown("""
<div style="background: rgba(255,255,255,0.05); backdrop-filter: blur(10px); border-radius: 20px; padding: 1.5rem; margin-bottom: 1.5rem; border: 1px solid rgba(255,255,255,0.1);">
    <h3 style="margin: 0 0 1rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; border-bottom: 2px solid #667eea; display: inline-block; padding-bottom: 0.5rem;">⚙️ Configuration</h3>
</div>
""", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    n_items = st.number_input("📦 Number of Items", min_value=1, max_value=500, value=3)

with col2:
    capacity = st.number_input("📀 Plate Capacity (UPS)", min_value=1, max_value=200, value=10)

with col3:
    max_plates = st.number_input("🎨 Max Plates", min_value=1, max_value=50, value=3)

with col4:
    addon_percent = st.number_input("📈 Add-on (%)", min_value=0.0, max_value=50.0, value=0.0, step=0.5)

with col5:
    job_number = st.text_input(
        "🔢 Job Number",
        value=f"JOB-{datetime.now().strftime('%d-%m-%Y_%H:%M')}",
        help="Enter a job number for tracking"
    )

# ================================================================
# MAIN CONTENT - Item Entry
# ================================================================
st.markdown("""
<div style="background: rgba(255,255,255,0.05); backdrop-filter: blur(10px); border-radius: 20px; padding: 1.5rem; margin-bottom: 1.5rem; border: 1px solid rgba(255,255,255,0.1);">
    <h3 style="margin: 0 0 1rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; border-bottom: 2px solid #667eea; display: inline-block; padding-bottom: 0.5rem;">📦 Item Details</h3>
</div>
""", unsafe_allow_html=True)

data = []
demand = {}
original_qty = {}

if input_method == "✏️ Manual Entry":
    cols = st.columns([0.5, 2, 2, 2, 2.5])
    cols[0].markdown("**SL**")
    cols[1].markdown("**Style**")
    cols[2].markdown("**Color**")
    cols[3].markdown("**Size**")
    cols[4].markdown("**Quantity**")
    
    for i in range(n_items):
        cols = st.columns([0.5, 2, 2, 2, 2.5])
        cols[0].markdown(f"**{i+1}**")
        style = cols[1].text_input("", key=f"style_{i}", placeholder="Style", label_visibility="collapsed")
        color = cols[2].text_input("", key=f"color_{i}", placeholder="Color", label_visibility="collapsed")
        size = cols[3].text_input("", key=f"size_{i}", placeholder="Size", label_visibility="collapsed")
        qty = cols[4].number_input("", key=f"qty_{i}", min_value=0, value=0, step=100, label_visibility="collapsed")
        
        if qty > 0:
            data.append({
                "SL": i+1,
                "Style": style or f"Item {i+1}",
                "Color": color or "N/A",
                "Size": size or "N/A",
                "Quantity": qty
            })

else:  # Upload Excel
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            
            # Remove completely empty rows
            df = df.dropna(how='all')
            
            # Auto-detect columns
            style_col = None
            color_col = None
            size_col = None
            qty_col = None
            sl_col = None
            
            for col in df.columns:
                col_lower = str(col).lower().strip()
                if col_lower in ['style', 'styles']:
                    style_col = col
                elif col_lower in ['color', 'colors', 'colour']:
                    color_col = col
                elif col_lower in ['size', 'sizes']:
                    size_col = col
                elif col_lower in ['quantity', 'qty', 'qty.', 'quantities', 'total']:
                    qty_col = col
                elif col_lower in ['sl', 's/l', 'serial', 'serial no', 'serial no.', 'no']:
                    sl_col = col
            
            if qty_col is None and len(df.columns) >= 2:
                for col in df.columns:
                    if df[col].dtype in ['int64', 'float64']:
                        qty_col = col
                        break
            
            if qty_col is None and len(df.columns) >= 2:
                qty_col = df.columns[-1]
            
            if style_col is None:
                style_col = df.columns[1] if len(df.columns) >= 2 else None
            if color_col is None:
                color_col = df.columns[2] if len(df.columns) >= 3 else None
            if size_col is None:
                size_col = df.columns[3] if len(df.columns) >= 4 else None
            
            if qty_col is None:
                st.error("❌ Could not find 'Quantity' column.")
                st.stop()
            
            sl_data = df[sl_col].tolist() if sl_col else list(range(1, len(df) + 1))
            style_data = df[style_col].astype(str).tolist() if style_col else ["N/A"] * len(df)
            color_data = df[color_col].astype(str).tolist() if color_col else ["N/A"] * len(df)
            size_data = df[size_col].astype(str).tolist() if size_col else ["N/A"] * len(df)
            qty_data = df[qty_col].tolist()
            
            cleaned_data = []
            style_list = []
            color_list = []
            size_list = []
            qty_list = []
            sl_list = []
            skipped_rows = 0
            
            for idx, (sl, style, color, size, qty) in enumerate(zip(sl_data, style_data, color_data, size_data, qty_data)):
                if pd.isna(qty):
                    skipped_rows += 1
                    continue
                
                try:
                    qty_int = int(float(qty))
                    if qty_int > 0:
                        style_val = str(style).strip() if not pd.isna(style) and str(style).strip() != '' else "N/A"
                        color_val = str(color).strip() if not pd.isna(color) and str(color).strip() != '' else "N/A"
                        size_val = str(size).strip() if not pd.isna(size) and str(size).strip() != '' else "N/A"
                        sl_val = int(sl) if not pd.isna(sl) and str(sl).strip() != '' else idx + 1
                        
                        cleaned_data.append((sl_val, style_val, color_val, size_val, qty_int))
                        sl_list.append(sl_val)
                        style_list.append(style_val)
                        color_list.append(color_val)
                        size_list.append(size_val)
                        qty_list.append(qty_int)
                    else:
                        skipped_rows += 1
                except (ValueError, TypeError):
                    skipped_rows += 1
                    continue
            
            if not cleaned_data:
                st.error("❌ No valid data found.")
                st.stop()
            
            preview_df = pd.DataFrame({
                "SL": sl_list,
                "Style": style_list,
                "Color": color_list,
                "Size": size_list,
                "Quantity": qty_list
            })
            
            st.success(f"✅ Loaded {len(cleaned_data)} items!")
            if skipped_rows > 0:
                st.warning(f"⚠️ {skipped_rows} rows skipped.")
            
            st.dataframe(preview_df, use_container_width=True)
            
            n = len(cleaned_data)
            tags = [f"Item {i+1}" for i in range(n)]
            qty = qty_list
            
            st.session_state['item_styles'] = {f"Item {i+1}": style_list[i] for i in range(n)}
            st.session_state['item_colors'] = {f"Item {i+1}": color_list[i] for i in range(n)}
            st.session_state['item_sizes'] = {f"Item {i+1}": size_list[i] for i in range(n)}
            
            for t, q in zip(tags, qty):
                if q > 0:
                    original_qty[t] = int(q)
                    demand[t] = math.ceil(int(q) * (1 + addon_percent / 100))
                    
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
            st.stop()
    else:
        st.info("📤 Please upload an Excel file.")

# Preview data from manual entry
if data:
    st.info(f"📊 Total items entered: {len(data)}")
    preview_df = pd.DataFrame(data)
    st.dataframe(preview_df, use_container_width=True, height=200)
    
    # Process manual data
    for item in data:
        tag = item["Style"]
        qty = item["Quantity"]
        if qty > 0:
            original_qty[tag] = int(qty)
            demand[tag] = math.ceil(int(qty) * (1 + addon_percent / 100))

# ================================================================
# GENERATE BUTTON
# ================================================================
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_clicked = st.button("🚀 Generate Plans", type="primary", use_container_width=True)

# ================================================================
# EXCEL REPORT GENERATOR
# ================================================================
def generate_excel_report(plates, demand, original_qty, algo_name, waste_percent, job_number=""):
    """Generate Excel report"""
    bio = BytesIO()
    
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        summary_df = build_full_summary(plates, demand, original_qty)
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        
        plate_rows = []
        total_sheets_sum = 0
        total_ups_sum = 0
        
        for idx, p in enumerate(plates, 1):
            total_ups = sum(p["layout"].values())
            plate_rows.append({
                "SL": idx,
                "Plate ID": p.get("name", f"Plate {idx}"),
                "Sheets Required": p.get("sheets", 0),
                "Total UPS": total_ups,
                "Layout": ", ".join([f"{k}:{v}" for k, v in p["layout"].items()])
            })
            total_sheets_sum += p.get("sheets", 0)
            total_ups_sum += total_ups
        
        plate_rows.append({
            "SL": "TOTAL",
            "Plate ID": "",
            "Sheets Required": total_sheets_sum,
            "Total UPS": total_ups_sum,
            "Layout": ""
        })
        
        plate_df = pd.DataFrame(plate_rows)
        plate_df.to_excel(writer, sheet_name="Plate Details", index=False)
        
        info_df = pd.DataFrame({
            "Property": ["Algorithm", "Waste %", "Total Plates", "Total Sheets", "Job Number", "Generated On"],
            "Value": [
                algo_name,
                waste_percent,
                len(plates),
                total_sheets_sum,
                job_number if job_number else "N/A",
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        })
        info_df.to_excel(writer, sheet_name="Info", index=False)
    
    bio.seek(0)
    return bio

# ================================================================
# PDF REPORT GENERATOR
# ================================================================
def generate_pdf_report(plates, demand, original_qty, algo_name, waste_percent, job_number=""):
    """Generate PDF report"""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4, landscape
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER
    except ImportError:
        return None
    
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=landscape(A4),
            rightMargin=25, leftMargin=25, topMargin=25, bottomMargin=25
        )
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle', parent=styles['Heading1'],
            fontSize=20, alignment=TA_CENTER,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=6,
            fontName='Helvetica-Bold'
        )
        job_style = ParagraphStyle(
            'JobStyle', parent=styles['Heading2'],
            fontSize=16, alignment=TA_CENTER,
            textColor=colors.HexColor('#764ba2'),
            spaceAfter=8,
            fontName='Helvetica-Bold'
        )
        subtitle_style = ParagraphStyle(
            'CustomSubtitle', parent=styles['Normal'],
            fontSize=12, alignment=TA_CENTER,
            textColor=colors.grey,
            spaceAfter=14,
            fontName='Helvetica'
        )
        section_header_style = ParagraphStyle(
            'SectionHeader', parent=styles['Heading2'],
            fontSize=16, alignment=TA_CENTER,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        footer_style = ParagraphStyle(
            'Footer', parent=styles['Normal'],
            fontSize=10, alignment=TA_CENTER,
            textColor=colors.grey,
            spaceTop=14,
            fontName='Helvetica'
        )
        
        story = []
        
        story.append(Paragraph("📊 Plate Ratio System - Report", title_style))
        if job_number:
            story.append(Paragraph(f"🔢 Job Number: {job_number}", job_style))
        story.append(Paragraph(
            f"Algorithm: {algo_name} | Waste: {waste_percent}% | "
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            subtitle_style
        ))
        story.append(Spacer(1, 12))
        
        # Summary table
        header_row = ["SL", "Tag", "Original", "With Add-on"]
        for p in plates:
            header_row.append(f"Plate {p['name']}")
        header_row.extend(["Total Prod.", "Excess", "Excess %"])
        
        summary_data = [header_row]
        
        sl = 1
        for tag in demand.keys():
            row = [str(sl), tag, str(original_qty.get(tag, 0)), str(demand[tag])]
            
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
        
        total_row = ["📊", "TOTAL", str(sum(original_qty.values())), str(sum(demand.values()))]
        
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
        
        main_table = Table(summary_data, repeatRows=1)
        main_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 11),
            ('ALIGN', (0, 1), (-1, -2), 'CENTER'),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f0fe')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        for i in range(1, len(summary_data) - 1):
            if i % 2 == 0:
                main_table.setStyle([('BACKGROUND', (0, i), (-1, i), colors.HexColor('#f8f9fa'))])
        
        story.append(main_table)
        story.append(Spacer(1, 18))
        
        # Plate details
        story.append(Paragraph("🧾 Plate Configuration Details", section_header_style))
        story.append(Spacer(1, 10))
        
        plate_data = [["SL", "Plate ID", "Sheets", "Total UPS"]]
        for idx, p in enumerate(plates, 1):
            plate_data.append([
                str(idx),
                p["name"],
                str(p["sheets"]),
                str(sum(p["layout"].values()))
            ])
        
        total_sheets = sum(p["sheets"] for p in plates)
        total_ups = sum(sum(p["layout"].values()) for p in plates)
        plate_data.append(["📊", "TOTAL", str(total_sheets), str(total_ups)])
        
        plate_table = Table(plate_data)
        plate_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 11),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e8f0fe')),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ]))
        
        story.append(plate_table)
        story.append(Spacer(1, 18))
        
        story.append(Paragraph(
            f"Report Generated by Plate Ratio System | Job: {job_number if job_number else 'N/A'} | Design by Ovi | All Rights Reserved",
            footer_style
        ))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    except Exception as e:
        return None

# ================================================================
# RESULTS SECTION
# ================================================================
if generate_clicked:
    if not demand:
        st.error("⚠️ Please enter at least one item with quantity > 0")
    else:
        with st.spinner(f"🔍 Running {len(ALGORITHM_REGISTRY)} algorithms..."):
            results = {}
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            algo_list = list(ALGORITHM_REGISTRY.items())
            for idx, (algo_name, _) in enumerate(algo_list):
                status_text.text(f"Running {algo_name}... ({idx+1}/{len(algo_list)})")
                try:
                    optimizer = get_algorithm(algo_name, demand, capacity, max_plates)
                    plates = optimizer.optimize()
                    if plates:
                        results[algo_name] = plates
                except Exception:
                    pass
                
                progress_bar.progress((idx + 1) / len(algo_list))
            
            progress_bar.empty()
            status_text.empty()
        
        if not results:
            st.error("❌ No algorithm succeeded!")
        else:
            comparison_data = []
            for algo_name, plates in results.items():
                if plates:
                    waste = calculate_waste_percent(plates, demand)
                    comparison_data.append({
                        "Algorithm": algo_name,
                        "Waste %": waste,
                        "Plates": len(plates),
                        "Sheets": sum(p.get("sheets", 0) for p in plates)
                    })
            
            comparison_df = pd.DataFrame(comparison_data).sort_values("Waste %")
            
            best_algo = comparison_df.iloc[0]["Algorithm"]
            best_waste = comparison_df.iloc[0]["Waste %"]
            best_plates = results[best_algo]
            
            # Validate plate capacity
            for plate in best_plates:
                layout = plate["layout"]
                total_ups = sum(layout.values())
                
                if total_ups != capacity:
                    while sum(layout.values()) > capacity:
                        max_tag = max(layout, key=layout.get)
                        if layout[max_tag] > 1:
                            layout[max_tag] -= 1
                        else:
                            break
                    
                    while sum(layout.values()) < capacity:
                        best_tag = max(demand.keys(), key=lambda t: demand.get(t, 0) / (layout.get(t, 1) + 1))
                        layout[best_tag] = layout.get(best_tag, 0) + 1
                    
                    plate["layout"] = layout
            
            st.markdown(f"""
            <div class="best-algo">
                <h2>🏆 BEST ALGORITHM: {best_algo}</h2>
                <p style="font-size: 1.5rem; margin: 0.5rem 0;">Waste: {best_waste}%</p>
                <p style="margin: 0;">Total Algorithms Tested: {len(results)}</p>
                <p style="margin: 0; font-size: 0.85rem; opacity: 0.8;">Job Number: {job_number}</p>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📊 All Algorithms Comparison", expanded=False):
                st.dataframe(comparison_df, use_container_width=True)
            
            # Best Algorithm Report
            st.markdown("---")
            st.markdown("## 📋 Best Algorithm Report")
            
            summary_df = build_full_summary(best_plates, demand, original_qty)
            
            if not summary_df.empty:
                if summary_df.iloc[-1]["Tag"] != "TOTAL":
                    total_row = {
                        "SL": "📊",
                        "Tag": "TOTAL",
                        "Original QTY": summary_df["Original QTY"].sum(),
                        "Produced (+Add-on)": summary_df["Produced (+Add-on)"].sum(),
                    }
                    
                    for col in summary_df.columns:
                        if col.startswith("Plate "):
                            total_row[col] = summary_df[col].sum()
                    
                    total_row["Total Produced QTY"] = summary_df["Total Produced QTY"].sum()
                    total_excess = summary_df["Excess"].sum()
                    total_row["Excess"] = total_excess
                    
                    total_produced_qty = total_row["Total Produced QTY"]
                    total_excess_percent = round((total_excess / total_produced_qty) * 100, 2) if total_produced_qty > 0 else 0
                    total_row["Excess %"] = f"{total_excess_percent}%"
                    
                    summary_df = pd.concat([summary_df, pd.DataFrame([total_row])], ignore_index=True)
            
            st.dataframe(summary_df, use_container_width=True, height=350)
            
            # Plate Details
            st.markdown("### 🧾 Plate Details")
            
            plate_rows = []
            total_sheets_sum = 0
            total_ups_sum = 0
            
            for idx, p in enumerate(best_plates, 1):
                total_ups = sum(p["layout"].values())
                plate_name_str = p.get("name", f"Plate {idx}")
                plate_rows.append({
                    "SL": idx,
                    "Plate ID": plate_name_str,
                    "Sheets": p.get("sheets", 0),
                    "Total UPS": total_ups,
                    "Layout": ", ".join([f"{k}:{v}" for k, v in p["layout"].items()])
                })
                total_sheets_sum += p.get("sheets", 0)
                total_ups_sum += total_ups
            
            plate_rows.append({
                "SL": "📊",
                "Plate ID": "**TOTAL**",
                "Sheets": total_sheets_sum,
                "Total UPS": total_ups_sum,
                "Layout": ""
            })
            
            plate_details_df = pd.DataFrame(plate_rows)
            st.dataframe(plate_details_df, use_container_width=True)
            
            # Download buttons
            st.markdown("---")
            st.markdown("## 📥 Download Reports")
            
            col1, col2 = st.columns(2)
            
            with col1:
                excel_buffer = generate_excel_report(best_plates, demand, original_qty, best_algo, best_waste, job_number)
                st.download_button(
                    "📊 Download Excel Report",
                    excel_buffer,
                    f"Plate_Ratio_Report_{job_number}_{datetime.now().strftime('%d-%m-%Y_%H-%M')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            
            with col2:
                pdf_buffer = generate_pdf_report(best_plates, demand, original_qty, best_algo, best_waste, job_number)
                if pdf_buffer:
                    st.download_button(
                        "📄 Download PDF Report",
                        pdf_buffer,
                        f"Plate_Ratio_Report_{job_number}_{datetime.now().strftime('%d-%m-%Y_%H-%M')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.info("ℹ️ PDF download requires reportlab. Install with: pip install reportlab")
            
            # ================================================================
            # VIEW ANY ALGORITHM REPORT
            # ================================================================
            if results:
                st.markdown("---")
                st.markdown("## 📊 View Any Algorithm Report")
                
                # Initialize session state for view
                if 'view_selected_algo' not in st.session_state:
                    st.session_state.view_selected_algo = list(results.keys())[0] if results else None
                if 'view_clicked' not in st.session_state:
                    st.session_state.view_clicked = False
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    selected_algo = st.selectbox(
                        "Select an algorithm to view its detailed report:",
                        options=list(results.keys()),
                        index=0,
                        key="algo_selector",
                        label_visibility="collapsed"
                    )
                    st.session_state.view_selected_algo = selected_algo
                
                with col2:
                    view_clicked = st.button("👁️ VIEW", key="view_algo_btn", use_container_width=True)
                    if view_clicked:
                        st.session_state.view_clicked = True
                
                # Show report if VIEW clicked
                if st.session_state.view_clicked and st.session_state.view_selected_algo:
                    selected_algo = st.session_state.view_selected_algo
                    selected_plates = results[selected_algo]
                    selected_waste = calculate_waste_percent(selected_plates, demand)
                    
                    st.markdown(f"""
                    <div style="background: linear-gradient(135deg, rgba(102,126,234,0.15) 0%, rgba(118,75,162,0.15) 100%); 
                                border-radius: 16px; padding: 1rem; margin-bottom: 1rem; 
                                border: 1px solid rgba(102,126,234,0.3);">
                        <p style="margin: 0; font-size: 1.1rem; font-weight: 600; color: #667eea;">
                            📊 {selected_algo}
                        </p>
                        <p style="margin: 0.25rem 0; font-size: 0.9rem; color: rgba(255,255,255,0.7);">
                            Waste: <strong style="color: #00b09b;">{selected_waste}%</strong> | 
                            Plates: <strong>{len(selected_plates)}</strong> | 
                            Sheets: <strong>{sum(p.get('sheets', 0) for p in selected_plates)}</strong>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Validate capacity
                    for plate in selected_plates:
                        layout = plate["layout"]
                        total_ups = sum(layout.values())
                        
                        if total_ups != capacity:
                            while sum(layout.values()) > capacity:
                                max_tag = max(layout, key=layout.get)
                                if layout[max_tag] > 1:
                                    layout[max_tag] -= 1
                                else:
                                    break
                            
                            while sum(layout.values()) < capacity:
                                best_tag = max(demand.keys(), key=lambda t: demand.get(t, 0) / (layout.get(t, 1) + 1))
                                layout[best_tag] = layout.get(best_tag, 0) + 1
                            
                            plate["layout"] = layout
                    
                    # Summary
                    st.markdown("### 📋 Report Summary")
                    selected_summary_df = build_full_summary(selected_plates, demand, original_qty)
                    
                    if not selected_summary_df.empty:
                        if selected_summary_df.iloc[-1]["Tag"] != "TOTAL":
                            total_row = {
                                "SL": "📊",
                                "Tag": "TOTAL",
                                "Original QTY": selected_summary_df["Original QTY"].sum(),
                                "Produced (+Add-on)": selected_summary_df["Produced (+Add-on)"].sum(),
                            }
                            
                            for col in selected_summary_df.columns:
                                if col.startswith("Plate "):
                                    total_row[col] = selected_summary_df[col].sum()
                            
                            total_row["Total Produced QTY"] = selected_summary_df["Total Produced QTY"].sum()
                            total_excess = selected_summary_df["Excess"].sum()
                            total_row["Excess"] = total_excess
                            
                            total_produced_qty = total_row["Total Produced QTY"]
                            total_excess_percent = round((total_excess / total_produced_qty) * 100, 2) if total_produced_qty > 0 else 0
                            total_row["Excess %"] = f"{total_excess_percent}%"
                            
                            selected_summary_df = pd.concat([selected_summary_df, pd.DataFrame([total_row])], ignore_index=True)
                    
                    st.dataframe(selected_summary_df, use_container_width=True, height=300)
                    
                    # Plate Details
                    st.markdown("### 🧾 Plate Details")
                    
                    selected_plate_rows = []
                    selected_total_sheets = 0
                    selected_total_ups = 0
                    
                    for idx, p in enumerate(selected_plates, 1):
                        total_ups = sum(p["layout"].values())
                        plate_name_str = p.get("name", f"Plate {idx}")
                        selected_plate_rows.append({
                            "SL": idx,
                            "Plate ID": plate_name_str,
                            "Sheets": p.get("sheets", 0),
                            "Total UPS": total_ups,
                            "Layout": ", ".join([f"{k}:{v}" for k, v in p["layout"].items()])
                        })
                        selected_total_sheets += p.get("sheets", 0)
                        selected_total_ups += total_ups
                    
                    selected_plate_rows.append({
                        "SL": "📊",
                        "Plate ID": "**TOTAL**",
                        "Sheets": selected_total_sheets,
                        "Total UPS": selected_total_ups,
                        "Layout": ""
                    })
                    
                    selected_plate_df = pd.DataFrame(selected_plate_rows)
                    st.dataframe(selected_plate_df, use_container_width=True)
                    
                    # Download for selected
                    st.markdown("### 📥 Download Selected Report")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        selected_excel = generate_excel_report(
                            selected_plates, demand, original_qty, 
                            selected_algo, selected_waste, job_number
                        )
                        st.download_button(
                            f"📊 Download {selected_algo} Excel",
                            selected_excel,
                            f"{selected_algo}_{job_number}_{datetime.now().strftime('%d-%m-%Y_%H-%M')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    
                    with col2:
                        selected_pdf = generate_pdf_report(
                            selected_plates, demand, original_qty, 
                            selected_algo, selected_waste, job_number
                        )
                        if selected_pdf:
                            st.download_button(
                                f"📄 Download {selected_algo} PDF",
                                selected_pdf,
                                f"{selected_algo}_{job_number}_{datetime.now().strftime('%d-%m-%Y_%H-%M')}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        else:
                            st.info("ℹ️ PDF download requires reportlab")
                    
                    # Close button
                    if st.button("❌ Close Report", key="close_view_btn"):
                        st.session_state.view_clicked = False
                        st.rerun()

# ================================================================
# FOOTER
# ================================================================
st.markdown("""
<div class="footer-border" style="text-align: center; padding: 2rem; margin-top: 3rem; border-top: 2px solid rgba(102,126,234,0.3); border-radius: 20px;">
    <p class="footer-text" style="margin: 0; font-size: 0.85rem;">
        © 2025 Plate Ratio System | Version 26 (Complete Edition)
    </p>
    <p class="footer-text" style="margin: 8px 0; font-size: 0.8rem;">
        26 Algorithms • Production Ready • AI-Powered
    </p>
    <p style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 0.85rem; font-weight: 600; margin: 10px 0 0 0;">
        ✨ Developed by Ovi | All Rights Reserved ✨
    </p>
</div>
""", unsafe_allow_html=True)
