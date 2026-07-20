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
from utils.auth import check_password
from utils.sidebar import render_sidebar
from utils.ui_components import render_header, render_footer
from utils.config_section import render_config
from utils.item_entry import render_manual_entry, render_excel_upload


# ================================================================
# CSS LOADER
# ================================================================
import os

def load_css():
    """Load CSS from static/css/style.css"""
    css_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "static",
        "css",
        "style.css"
    )

    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            return f"<style>{f.read()}</style>"

    return ""

# ================================================================
# APPLY CSS
# ================================================================
st.markdown(load_css(), unsafe_allow_html=True)

# ================================================================
# IMPORT PDF GENERATOR
# ================================================================
try:
    from utils.pdf_generator import generate_pdf_report
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

    def generate_pdf_report(*args, **kwargs):
        return None


# ================================================================
# IMPORT EXCEL GENERATOR (from utils)
# ================================================================
try:
    from utils.excel_generator import generate_excel_report
    EXCEL_AVAILABLE = True
except ImportError:
    EXCEL_AVAILABLE = False
    def generate_excel_report(*args, **kwargs):
        return None
# ================================================================
# STREAMLIT PAGE CONFIGURATION
# ================================================================
st.set_page_config(
    page_title="Plate Ratio System - Complete Edition",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)


# ================== APP START ==================
if not check_password():
    st.stop()

# ================================================================
# SIDEBAR - শুধু Input Method
# ================================================================
input_method = render_sidebar()

# ================================================================
# PLATE VALIDATION FUNCTION
# ================================================================
def validate_plate_capacity(plates, capacity):
    """
    Validate that each plate's total UPS equals the plate capacity
    If not, fix the layout to match capacity
    """
    if not plates:
        return plates
    
    for plate in plates:
        layout = plate["layout"]
        total_ups = sum(layout.values())
        
        # If total UPS doesn't match capacity, fix it
        if total_ups != capacity:
            # If more than capacity, remove from tags with highest UPS
            while sum(layout.values()) > capacity:
                max_tag = max(layout, key=layout.get)
                if layout[max_tag] > 1:
                    layout[max_tag] -= 1
                else:
                    # If all are 1, remove from the tag with lowest demand
                    min_tag = min(layout.keys(), key=lambda t: layout.get(t, 0))
                    if layout.get(min_tag, 0) > 0:
                        layout[min_tag] = 0
                    else:
                        break
            
            # If less than capacity, add to tags with highest demand
            while sum(layout.values()) < capacity:
                # Find tag with highest demand relative to current UPS
                best_tag = max(layout.keys(), key=lambda t: demand.get(t, 0) / (layout.get(t, 1) + 1))
                layout[best_tag] = layout.get(best_tag, 0) + 1
            
            plate["layout"] = layout
    
    return plates


        
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

# ================================================================
# MAIN CONTENT - Configuration (৫ কলাম)
# ================================================================
n_items, capacity, max_plates, addon_percent, job_number = render_config()
# ================================================================
# MAIN CONTENT - Item Entry
# ================================================================
data = []
original_qty = {}
demand = {}

if input_method == "✏️ Manual Entry":
    data = render_manual_entry(n_items)
else:
    original_qty, demand = render_excel_upload(addon_percent)


# ================================================================
# GENERATE BUTTON
# ================================================================
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    generate_clicked = st.button("🚀 Generate Plans", type="primary", use_container_width=True)

# ================================================================
# RESULTS SECTION
# ================================================================
if generate_clicked:
    # Check if data exists (either from manual entry or Excel upload)
    if not data and not demand:
        st.error("⚠️ Please enter at least one item with quantity > 0")
    else:
        # If data is empty but demand has values (from Excel upload)
        if not data and demand:
            pass  # demand already has values from Excel
        
        # If data has values (from manual entry), process it
        elif data:
            demand = {}
            original_qty = {}
            
            for item in data:
                tag = item["Style"]
                qty = item["Quantity"]
                if qty > 0:
                    demand[tag] = int(qty * (1 + addon_percent / 100))
                    original_qty[tag] = int(qty)
        
        if not demand:
            st.error("⚠️ No valid data found!")
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
                
                # ================================================================
                # VALIDATE PLATE CAPACITY
                # ================================================================
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
                
                # ================================================================
                # BEST ALGORITHM REPORT
                # ================================================================
                st.markdown("---")
                st.markdown("## 📋 Best Algorithm Report")

                # Get style/color/size from session state
                styles_dict = st.session_state.get('item_styles', {})
                colors_dict = st.session_state.get('item_colors', {})
                sizes_dict = st.session_state.get('item_sizes', {})

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
                    })
                    total_sheets_sum += p.get("sheets", 0)
                    total_ups_sum += total_ups

                plate_rows.append({
                    "SL": "📊",
                    "Plate ID": "**TOTAL**",
                    "Sheets": total_sheets_sum,
                    "Total UPS": total_ups_sum,
                })

                plate_details_df = pd.DataFrame(plate_rows)
                st.dataframe(plate_details_df, use_container_width=True)
                
                # ================================================================
                # REPORT DOWNLOAD BUTTONS
                # ================================================================
                st.markdown("---")
                st.markdown("## 📥 Download Reports")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    excel_buffer = generate_excel_report(
                        best_plates, 
                        demand, 
                        original_qty, 
                        best_algo, 
                        best_waste, 
                        job_number
                    )
                    
                    if excel_buffer is not None:
                        st.download_button(
                            "📊 Download Excel Report",
                            excel_buffer,
                            f"Plate_Ratio_Report_{job_number}_{datetime.now().strftime('%d-%m-%Y_%H-%M')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                    else:
                        st.error("❌ Excel report could not be generated. Please check the data.")
                
                with col2:
                    # Get style/color/size from session state
                    styles_dict = st.session_state.get('item_styles', {})
                    colors_dict = st.session_state.get('item_colors', {})
                    sizes_dict = st.session_state.get('item_sizes', {})
                    
                    pdf_buffer = generate_pdf_report(
                        best_plates, 
                        demand, 
                        original_qty, 
                        best_algo, 
                        best_waste, 
                        job_number,
                        styles_dict,
                        colors_dict,
                        sizes_dict
                    )
                    
                    if pdf_buffer is not None:
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
