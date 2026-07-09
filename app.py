"""
Plate Ratio System - Complete Edition
Main Streamlit Application
"""

import sys
import os
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import math

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import algorithms
from algorithms import ALGORITHM_REGISTRY, get_algorithm
from utils.helpers import ensure_demand_met, calculate_waste_percent, build_full_summary
from utils.pdf_generator import generate_pdf_report
from utils.excel_generator import generate_excel_report

# Page config
st.set_page_config(
    page_title="Plate Ratio System",
    page_icon="📊",
    layout="wide"
)

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
            .designer-name {
                color: rgba(255,255,255,0.7) !important;
                font-size: 0.85rem;
            }
            .best-algo {
                background: linear-gradient(135deg, #00b09b 0%, #96c93d 100%);
                padding: 1.5rem;
                border-radius: 20px;
                text-align: center;
                color: white;
                margin: 1rem 0;
            }
            .footer-border {
                text-align: center;
                padding: 2rem;
                margin-top: 3rem;
                border-top: 2px solid #667eea;
            }
        </style>
        """, unsafe_allow_html=True)

# ================================================================
# MAIN APP
# ================================================================
def main():
    # Load custom CSS
    load_css()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>📊 Plate Ratio Intelligence System</h1>
        <p>Complete Edition • 26 Algorithms • Production Ready</p>
        <p style="font-size: 0.85rem; opacity: 0.8;">AI-Powered • Fast • Accurate</p>
        <p class="designer-name">✨ Design by Ovi ✨</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # Input method
        input_method = st.radio(
            "📥 Input Method",
            ["✏️ Manual Entry", "📂 Upload Excel"],
            index=0
        )
        
        # Common parameters
        st.markdown("---")
        st.markdown("### 📐 Production Settings")
        
        capacity = st.number_input("Plate Capacity (UPS)", min_value=1, max_value=200, value=10, help="Units Per Sheet")
        max_plates = st.number_input("Max Plates", min_value=1, max_value=50, value=3, help="Maximum number of plates")
        addon_percent = st.number_input("Add-on (%)", min_value=0.0, max_value=50.0, value=0.0, step=0.5, help="Safety stock percentage")
        
        st.markdown("---")
        job_number = st.text_input("🔢 Job Number", value=f"JOB-{datetime.now().strftime('%Y%m%d_%H%M')}")
        
        st.markdown("---")
        st.markdown("### 📊 About")
        st.markdown("""
        This system uses **26 different algorithms** to find the optimal plate ratio.
        Each algorithm uses different optimization techniques.
        """)
        st.markdown("""
        **Algorithms:**
        - V1-V8: Classical Methods
        - V11-V18: Evolutionary Methods
        - V19-V26: AI & ML Methods
        """)
    
    # Main content area
    data = []
    
    if input_method == "✏️ Manual Entry":
        st.markdown("### 📦 Manual Item Entry")
        n_items = st.number_input("Number of Items", min_value=1, max_value=500, value=3)
        
        st.markdown("---")
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
        st.markdown("### 📂 Upload Excel File")
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1rem; border-radius: 10px; margin-bottom: 1rem;">
            <p style="margin: 0; color: #333;">📌 <strong>Required columns:</strong> Style, Color, Size, Quantity</p>
            <p style="margin: 0; color: #666; font-size: 0.85rem;">File should be in .xlsx or .xls format</p>
        </div>
        """, unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
        
        if uploaded_file:
            try:
                df = pd.read_excel(uploaded_file)
                
                # Auto-detect columns
                style_col = None
                color_col = None
                size_col = None
                qty_col = None
                
                for col in df.columns:
                    col_lower = str(col).lower().strip()
                    if col_lower in ['style', 'styles', 'item']:
                        style_col = col
                    elif col_lower in ['color', 'colors', 'colour']:
                        color_col = col
                    elif col_lower in ['size', 'sizes']:
                        size_col = col
                    elif col_lower in ['quantity', 'qty', 'qty.', 'total']:
                        qty_col = col
                
                # Fallback: use columns by position
                if qty_col is None and len(df.columns) >= 4:
                    qty_col = df.columns[-1]
                    style_col = df.columns[0]
                    color_col = df.columns[1] if len(df.columns) > 1 else None
                    size_col = df.columns[2] if len(df.columns) > 2 else None
                
                if qty_col is None:
                    st.error("❌ Could not find 'Quantity' column. Please ensure your file has a quantity column.")
                    st.stop()
                
                # Process data
                for idx, row in df.iterrows():
                    try:
                        qty = int(float(row[qty_col])) if not pd.isna(row[qty_col]) else 0
                        if qty > 0:
                            style = str(row[style_col]) if style_col and not pd.isna(row[style_col]) else f"Item {idx+1}"
                            color = str(row[color_col]) if color_col and not pd.isna(row[color_col]) else "N/A"
                            size = str(row[size_col]) if size_col and not pd.isna(row[size_col]) else "N/A"
                            
                            data.append({
                                "SL": idx+1,
                                "Style": style,
                                "Color": color,
                                "Size": size,
                                "Quantity": qty
                            })
                    except:
                        continue
                
                if data:
                    st.success(f"✅ Loaded {len(data)} items successfully!")
                    preview_df = pd.DataFrame(data)
                    st.dataframe(preview_df, use_container_width=True)
                else:
                    st.warning("⚠️ No valid data found in the file.")
                    
            except Exception as e:
                st.error(f"❌ Error reading file: {str(e)}")
    
    # Generate button
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        generate_clicked = st.button("🚀 Generate Plans", type="primary", use_container_width=True)
    
    if generate_clicked:
        if not data:
            st.error("⚠️ Please enter at least one item with quantity > 0")
            return
        
        # Process data
        demand = {}
        original_qty = {}
        styles_dict = {}
        colors_dict = {}
        sizes_dict = {}
        
        for item in data:
            tag = item["Style"]
            qty = item["Quantity"]
            if qty > 0:
                demand[tag] = int(qty * (1 + addon_percent / 100))
                original_qty[tag] = int(qty)
                styles_dict[tag] = item["Style"]
                colors_dict[tag] = item["Color"]
                sizes_dict[tag] = item["Size"]
        
        if not demand:
            st.error("⚠️ No valid data found!")
            return
        
        # Show demand summary
        with st.expander("📊 Demand Summary", expanded=True):
            demand_df = pd.DataFrame({
                "Item": list(demand.keys()),
                "Original QTY": [original_qty[k] for k in demand.keys()],
                "With Add-on": [demand[k] for k in demand.keys()],
                "Style": [styles_dict[k] for k in demand.keys()],
                "Color": [colors_dict[k] for k in demand.keys()],
                "Size": [sizes_dict[k] for k in demand.keys()]
            })
            st.dataframe(demand_df, use_container_width=True)
        
        # Run all algorithms
        with st.spinner("🔍 Running all 26 algorithms... This may take a moment."):
            results = {}
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            algo_list = list(ALGORITHM_REGISTRY.items())
            for idx, (algo_name, _) in enumerate(algo_list):
                status_text.text(f"Running {algo_name}... ({idx+1}/{len(algo_list)})")
                try:
                    optimizer = get_algorithm(algo_name, demand, capacity, max_plates)
                    plates = optimizer.optimize()
                    results[algo_name] = plates
                except Exception as e:
                    st.warning(f"⚠️ {algo_name} failed: {str(e)}")
                    # Use V3 as fallback
                    try:
                        optimizer = get_algorithm("V3 - Smart Decimal Balancing", demand, capacity, max_plates)
                        results[algo_name] = optimizer.optimize()
                    except:
                        results[algo_name] = None
                
                progress_bar.progress((idx + 1) / len(algo_list))
            
            progress_bar.empty()
            status_text.empty()
        
        # Filter out None results
        results = {k: v for k, v in results.items() if v is not None}
        
        if not results:
            st.error("❌ All algorithms failed! Please check your input data.")
            return
        
        # Find best algorithm
        comparison_data = []
        for algo_name, plates in results.items():
            if plates:
                waste = calculate_waste_percent(plates, demand)
                total_sheets = sum(p.get("sheets", 0) for p in plates)
                comparison_data.append({
                    "Algorithm": algo_name,
                    "Waste %": waste,
                    "Total Plates": len(plates),
                    "Total Sheets": total_sheets
                })
        
        comparison_df = pd.DataFrame(comparison_data).sort_values("Waste %")
        best_algo = comparison_df.iloc[0]["Algorithm"]
        best_waste = comparison_df.iloc[0]["Waste %"]
        best_plates = results[best_algo]
        
        # Display best algorithm
        st.markdown(f"""
        <div class="best-algo">
            <h2>🏆 BEST ALGORITHM: {best_algo}</h2>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">Waste: {best_waste}%</p>
            <p style="margin: 0;">Total Algorithms Tested: {len(results)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display comparison table
        with st.expander("📊 All Algorithms Comparison", expanded=False):
            st.dataframe(
                comparison_df.style.background_gradient(subset=["Waste %"], cmap="RdYlGn_r"),
                use_container_width=True
            )
        
        # Display best algorithm report
        if best_plates:
            st.markdown("---")
            st.markdown("## 📋 Best Algorithm Report")
            
            # Summary
            summary_df = build_full_summary(best_plates, demand, original_qty)
            st.dataframe(summary_df, use_container_width=True, height=300)
            
            # Plate details
            st.markdown("### 🧾 Plate Configuration Details")
            plate_rows = []
            total_sheets_sum = 0
            total_ups_sum = 0
            
            for idx, p in enumerate(best_plates, 1):
                if p and "layout" in p:
                    total_ups = sum(p["layout"].values())
                    plate_name_str = p.get("name", f"Plate {idx}")
                    plate_rows.append({
                        "SL": idx,
                        "Plate ID": plate_name_str,
                        "Sheets Required": p.get("sheets", 0),
                        "Total UPS": total_ups,
                        "Layout": ", ".join([f"{k}:{v}" for k, v in p["layout"].items()])
                    })
                    total_sheets_sum += p.get("sheets", 0)
                    total_ups_sum += total_ups
            
            plate_rows.append({
                "SL": "📊",
                "Plate ID": "TOTAL",
                "Sheets Required": total_sheets_sum,
                "Total UPS": total_ups_sum,
                "Layout": "-"
            })
            
            plate_details_df = pd.DataFrame(plate_rows)
            st.dataframe(plate_details_df, use_container_width=True)
            
            # Download buttons
            st.markdown("---")
            st.markdown("### 📥 Download Reports")
            
            col1, col2 = st.columns(2)
            
            with col1:
                excel_buffer = generate_excel_report(best_plates, demand, original_qty, best_algo, best_waste)
                st.download_button(
                    "📊 Download Excel Report",
                    excel_buffer,
                    f"{job_number}_report.xlsx",
                    use_container_width=True
                )
            
            with col2:
                pdf_buffer = generate_pdf_report(
                    best_plates, demand, original_qty, best_algo, best_waste,
                    styles_dict, colors_dict, sizes_dict, job_number
                )
                if pdf_buffer:
                    st.download_button(
                        "📄 Download PDF Report",
                        pdf_buffer,
                        f"{job_number}_report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.warning("⚠️ PDF generation failed. Install reportlab: pip install reportlab")
    
    # Footer
    st.markdown("""
    <div class="footer-border">
        <p style="margin: 0; font-size: 0.85rem; color: #666;">
            © 2025 Plate Ratio System | Version 26 (Complete Edition)
        </p>
        <p style="margin: 8px 0; font-size: 0.8rem; color: #888;">
            Enterprise Production Optimization Framework • 26 Algorithms • Production Ready
        </p>
        <p style="color: #667eea; font-size: 0.85rem; font-weight: 600; margin: 10px 0 0 0;">
            ✨ Developed by Ovi | All Rights Reserved ✨
        </p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
