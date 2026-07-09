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
    initial_sidebar_state="collapsed"
)

# ================================================================
# PASSWORD AUTHENTICATION
# ================================================================
def check_password():
    expected = None
    try:
        expected = st.secrets.get("app_password", None)
    except Exception:
        pass
    
    if expected is None:
        expected = os.environ.get("PEPCO_APP_PASSWORD")
    
    if expected is None:
        st.error("App password not configured.")
        return False

    def _password_entered():
        if st.session_state.get("password") == expected:
            st.session_state["password_correct"] = True
            try:
                del st.session_state["password"]
            except Exception:
                pass
        else:
            st.session_state["password_correct"] = False
            st.session_state["wrong_password"] = True

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
        st.error("❌ Incorrect password. Please contact Mr. Ovi.")

    return False

# ================== APP START ==================
if not check_password():
    st.stop()

# ================================================================
# MODERN CSS FOR MAIN APP (Light + Dark Mode Compatible)
# ================================================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    * { font-family: 'Inter', sans-serif; }
    
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 50%, #24243e 100%);
    }
    
    .stApp, .stApp p, .stApp div, .stApp span, .stApp label {
        color: rgba(255,255,255,0.9) !important;
    }
    
    .main-header {
        background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid rgba(255,255,255,0.1);
        padding: 2rem 2rem;
        margin-bottom: 2rem;
        text-align: center;
        border-radius: 0;
    }
    .main-header h1 {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    .main-header p { color: rgba(255,255,255,0.7) !important; margin-top: 0.5rem; }
    
    .card {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.3s ease;
    }
    .card:hover { border-color: rgba(102,126,234,0.5); box-shadow: 0 8px 32px rgba(0,0,0,0.2); }
    .card-title {
        font-size: 1.2rem;
        font-weight: 600;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        border-bottom: 2px solid #667eea;
        display: inline-block;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
    }
    
    .stNumberInput input, .stTextInput input {
        background: rgba(255,255,255,0.08) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 5px !important;
        color: white !important;
        padding: 0.5rem 1rem !important;
    }
    .stNumberInput input:focus, .stTextInput input:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102,126,234,0.2) !important;
        background: rgba(255,255,255,0.12) !important;
    }
    
    .stSelectbox label, .stNumberInput label, .stTextInput label, .stRadio label {
        color: rgba(255,255,255,0.9) !important;
    }
    .stRadio div[role="radiogroup"] {
        color: rgba(255,255,255,0.9) !important;
    }
    .stRadio div[role="radiogroup"] label {
        color: rgba(255,255,255,0.9) !important;
    }
    
    .stDataFrame { background: rgba(255,255,255,0.05); border-radius: 16px; padding: 0.5rem; }
    .stDataFrame table { color: rgba(255,255,255,0.9) !important; }
    .stDataFrame thead tr th { background: rgba(102,126,234,0.2) !important; color: rgba(255,255,255,0.9) !important; }
    .stDataFrame tbody tr td { color: rgba(255,255,255,0.9) !important; }
    
    .stAlert { background: rgba(255,255,255,0.05) !important; }
    .stAlert p, .stAlert div { color: rgba(255,255,255,0.9) !important; }
    
    .stExpander { background: rgba(255,255,255,0.05) !important; border: 1px solid rgba(255,255,255,0.1) !important; }
    .stExpander summary { color: rgba(255,255,255,0.9) !important; }
    
    .tag-display {
        background: linear-gradient(135deg, rgba(102,126,234,0.2) 0%, rgba(118,75,162,0.2) 100%);
        padding: 10px;
        border-radius: 12px;
        border: 1px solid rgba(102,126,234,0.3);
        color: #667eea;
        font-weight: 600;
        text-align: center;
        font-size: 0.9rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, rgba(102,126,234,0.2) 0%, rgba(118,75,162,0.2) 100%);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        padding: 1rem;
        color: white;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .metric-label { font-size: 0.85rem; color: rgba(255,255,255,0.7) !important; margin-top: 0.5rem; }
    
    .best-algo {
        background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
        border-radius: 20px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        border: none;
        box-shadow: 0 10px 30px rgba(0,176,155,0.3);
        margin-bottom: 2rem;
    }
    .best-algo .metric-value { -webkit-text-fill-color: white; font-size: 1.5rem; }
    .best-algo .metric-label { color: rgba(255,255,255,0.9) !important; }
    
    .stButton > button, .stDownloadButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        font-size: 1rem !important;
    }
    .stButton > button:hover, .stDownloadButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 20px rgba(102,126,234,0.4) !important;
    }
    
    .warning { background: rgba(255,193,7,0.1) !important; padding: 12px; border-radius: 12px; border-left: 4px solid #ffc107 !important; color: #ffc107 !important; margin: 1rem 0; }
    .info { background: rgba(23,162,184,0.1) !important; padding: 12px; border-radius: 12px; border-left: 4px solid #17a2b8 !important; color: #17a2b8 !important; }
    
    ::-webkit-scrollbar { width: 8px; height: 8px; }
    ::-webkit-scrollbar-track { background: rgba(255,255,255,0.05); border-radius: 10px; }
    ::-webkit-scrollbar-thumb { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; }
    
    .stSuccess, .stInfo, .stWarning, .stError {
        background: rgba(255,255,255,0.05) !important;
    }
    .stSuccess p, .stInfo p, .stWarning p, .stError p {
        color: rgba(255,255,255,0.9) !important;
    }
    
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4, .stMarkdown h5, .stMarkdown h6 {
        color: rgba(255,255,255,0.9) !important;
    }
    .stMarkdown strong, .stMarkdown b {
        color: rgba(255,255,255,0.9) !important;
    }
    
    .footer-text { color: rgba(255,255,255,0.6) !important; }
    .footer-border { border-top: 2px solid rgba(102,126,234,0.3) !important; background: rgba(255,255,255,0.02) !important; }
    
    @media (prefers-color-scheme: light) {
        .stApp { background: linear-gradient(135deg, #f0f2f5 0%, #e8ecf1 100%); }
        .stApp, .stApp p, .stApp div, .stApp span, .stApp label,
        .stMarkdown, .stMarkdown p, .stMarkdown div, .stMarkdown span,
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4,
        .stMarkdown strong, .stMarkdown b { color: #1a1a3e !important; }
        .main-header { background: rgba(255,255,255,0.9) !important; border-bottom: 1px solid rgba(0,0,0,0.1) !important; }
        .main-header p { color: rgba(0,0,0,0.7) !important; }
        .card { background: rgba(255,255,255,0.95) !important; border: 1px solid rgba(0,0,0,0.08) !important; box-shadow: 0 2px 10px rgba(0,0,0,0.05) !important; }
        .stNumberInput input, .stTextInput input { background: white !important; border: 1px solid rgba(0,0,0,0.2) !important; color: #1a1a3e !important; }
        .stDataFrame { background: white !important; }
        .stDataFrame table { color: #1a1a3e !important; }
        .stDataFrame thead tr th { background: rgba(102,126,234,0.1) !important; color: #1a1a3e !important; }
        .stDataFrame tbody tr td { color: #1a1a3e !important; }
        .stAlert { background: white !important; }
        .stExpander { background: white !important; border: 1px solid rgba(0,0,0,0.08) !important; }
        .tag-display { background: rgba(102,126,234,0.08) !important; color: #4a3f8a !important; }
        .metric-card { background: white !important; border: 1px solid rgba(0,0,0,0.08) !important; color: #1a1a3e !important; }
        .warning { background: rgba(255,193,7,0.15) !important; color: #856404 !important; }
        .info { background: rgba(23,162,184,0.15) !important; color: #0c5460 !important; }
        .stSuccess { background: #d4edda !important; }
        .stSuccess p { color: #155724 !important; }
        .stInfo { background: #d1ecf1 !important; }
        .stInfo p { color: #0c5460 !important; }
        .stWarning { background: #fff3cd !important; }
        .stWarning p { color: #856404 !important; }
        .stError { background: #f8d7da !important; }
        .stError p { color: #721c24 !important; }
    }
</style>
""", unsafe_allow_html=True)

# ================================================================
# SIDEBAR - Input Method
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
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(118,75,162,0.1) 100%); border-radius: 10px; padding: 0.75rem; text-align: center; border: 1px solid rgba(102,126,234,0.2);">
        <p style="margin: 0; font-size: 0.75rem; color: rgba(255,255,255,0.5);">🧠 {len(ALGORITHM_REGISTRY)} Algorithms</p>
        <p style="margin: 0; font-size: 0.65rem; color: rgba(255,255,255,0.3);">V1 - V26 Complete</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    with st.expander("📊 About", expanded=False):
        st.markdown("""
        **26 Algorithms:**
        - V1-V10: Classical
        - V11-V18: Evolutionary
        - V19-V26: AI & ML
        """)

# ================================================================
# MAIN CONTENT - Header
# ================================================================
st.markdown("""
<div class="main-header">
    <h1>📊 Plate Ratio Intelligence System</h1>
    <p>Complete Edition • 26 Algorithms • Production Ready</p>
    <p style="font-size: 0.85rem; opacity: 0.8;">AI-Powered • Fast • Accurate</p>
    <p style="color: rgba(255,255,255,0.6); font-size: 0.85rem;">✨ Design by Ovi ✨</p>
</div>
""", unsafe_allow_html=True)

# Configuration
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
    job_number = st.text_input("🔢 Job Number", value=f"JOB-{datetime.now().strftime('%d-%m-%Y_%H-%M')}")

st.markdown("""
<div style="background: rgba(255,255,255,0.05); backdrop-filter: blur(10px); border-radius: 20px; padding: 1.5rem; margin-bottom: 1.5rem; border: 1px solid rgba(255,255,255,0.1);">
    <h3 style="margin: 0 0 1rem 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; border-bottom: 2px solid #667eea; display: inline-block; padding-bottom: 0.5rem;">📦 Item Details</h3>
</div>
""", unsafe_allow_html=True)

# ডাটাস্ট্রাকচার ইনিশিয়ালাইজেশন
final_demand = {}
final_original_qty = {}
has_valid_data = False

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
            tag = style or f"Item {i+1}"
            final_original_qty[tag] = int(qty)
            final_demand[tag] = math.ceil(int(qty) * (1 + addon_percent / 100))
            has_valid_data = True

# ================== EXCEL FILE UPLOAD ==================
else:
    st.markdown('<div class="card"><div class="card-title" style="text-align: center; display: block; width: 100%;">📂 Upload Excel File</div>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader("Upload Excel file with Item Details", type=["xlsx", "xls"])
    
    if uploaded_file is not None:
        try:
            df = pd.read_excel(uploaded_file).dropna(how='all')
            style_col, color_col, size_col, qty_col, sl_col = None, None, None, None, None
            
            for col in df.columns:
                col_lower = str(col).lower().strip()
                if col_lower in ['style', 'styles']: style_col = col
                elif col_lower in ['color', 'colors', 'colour']: color_col = col
                elif col_lower in ['size', 'sizes']: size_col = col
                elif col_lower in ['quantity', 'qty', 'qty.', 'quantities', 'total']: qty_col = col
                elif col_lower in ['sl', 's/l', 'serial', 'serial no', 'serial no.', 'no']: sl_col = col
            
            if qty_col is None and len(df.columns) >= 2:
                for col in df.columns:
                    if df[col].dtype in ['int64', 'float64']:
                        qty_col = col
                        break
            if qty_col is None: qty_col = df.columns[-1]
            if style_col is None: style_col = df.columns[1] if len(df.columns) >= 2 else None
            if color_col is None: color_col = df.columns[2] if len(df.columns) >= 3 else None
            if size_col is None: size_col = df.columns[3] if len(df.columns) >= 4 else None
            
            sl_data = df[sl_col].tolist() if sl_col else list(range(1, len(df) + 1))
            style_data = df[style_col].astype(str).tolist() if style_col else ["N/A"] * len(df)
            color_data = df[color_col].astype(str).tolist() if color_col else ["N/A"] * len(df)
            size_data = df[size_col].astype(str).tolist() if size_col else ["N/A"] * len(df)
            qty_data = df[qty_col].tolist()
            
            preview_rows = []
            for idx, (sl, style, color, size, qty) in enumerate(zip(sl_data, style_data, color_data, size_data, qty_data)):
                if pd.isna(qty): continue
                try:
                    qty_int = int(float(qty))
                    if qty_int > 0:
                        s_val = str(style).strip() if not pd.isna(style) and str(style).strip() != '' else f"Item {idx+1}"
                        preview_rows.append({"SL": sl, "Style": s_val, "Color": color, "Size": size, "Quantity": qty_int})
                        
                        final_original_qty[s_val] = qty_int
                        final_demand[s_val] = math.ceil(qty_int * (1 + addon_percent / 100))
                        has_valid_data = True
                except: continue
                
            if preview_rows:
                st.success(f"✅ File loaded successfully! {len(preview_rows)} items found.")
                st.dataframe(pd.DataFrame(preview_rows), use_container_width=True)
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
    else:
        st.info("📤 Please upload an Excel file.")

# ================================================================
# GENERATE BUTTON & PROCESSING
# ================================================================
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_clicked = st.button("🚀 Generate Plans", type="primary", use_container_width=True)

if generate_clicked:
    if not has_valid_data:
        st.error("⚠️ Please enter at least one item with quantity > 0")
    else:
        with st.spinner(f"🔍 Running {len(ALGORITHM_REGISTRY)} algorithms..."):
            results = {}
            algo_list = list(ALGORITHM_REGISTRY.items())
            for algo_name, _ in algo_list:
                try:
                    optimizer = get_algorithm(algo_name, final_demand, capacity, max_plates)
                    plates = optimizer.optimize()
                    if plates: results[algo_name] = plates
                except: pass
        
        if not results:
            st.error("❌ No algorithm succeeded!")
        else:
            comparison_data = []
            for algo_name, plates in results.items():
                if plates:
                    waste = calculate_waste_percent(plates, final_demand)
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
            
            # Fix layouts to match exact plate capacity
            for plate in best_plates:
                layout = plate["layout"]
                while sum(layout.values()) > capacity:
                    max_tag = max(layout, key=layout.get)
                    if layout[max_tag] > 1: layout[max_tag] -= 1
                    else: break
                while sum(layout.values()) < capacity:
                    best_tag = max(final_demand.keys(), key=lambda t: final_demand.get(t, 0) / (layout.get(t, 0) + 1))
                    layout[best_tag] = layout.get(best_tag, 0) + 1
                plate["layout"] = layout
            
            st.markdown(f"""
            <div class="best-algo">
                <h2>🏆 BEST ALGORITHM: {best_algo}</h2>
                <p style="font-size: 1.5rem; margin: 0.5rem 0;">Waste: {best_waste}%</p>
                <p style="margin: 0;">Job Number: {job_number}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Show Reports
            summary_df = build_full_summary(best_plates, final_demand, final_original_qty)
            st.dataframe(summary_df, use_container_width=True)
