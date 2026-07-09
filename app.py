"""
Plate Ratio System - Complete Edition
Main Streamlit Application
"""

import os
import sys
import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import algorithms
from algorithms import ALGORITHM_REGISTRY, get_algorithm
from utils.helpers import ensure_demand_met, create_valid_layout
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
    with open("static/css/style.css", "r") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

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
        <p style="font-size: 0.85rem; opacity: 0.6;">AI-Powered • Fast • Accurate</p>
        <p class="designer-name">✨ Design by Ovi ✨</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar for configuration
    with st.sidebar:
        st.markdown("## ⚙️ Configuration")
        
        # Input method
        input_method = st.radio(
            "Input Method",
            ["Manual Entry", "Upload Excel"],
            index=0
        )
        
        # Common parameters
        capacity = st.number_input("Plate Capacity (UPS)", min_value=1, max_value=200, value=10)
        max_plates = st.number_input("Max Plates", min_value=1, max_value=50, value=3)
        addon_percent = st.number_input("Add-on (%)", min_value=0.0, max_value=50.0, value=0.0, step=0.5)
        job_number = st.text_input("Job Number", value=f"JOB-{datetime.now().strftime('%Y%m%d_%H%M')}")
        
        st.markdown("---")
        st.markdown("### 📊 About")
        st.markdown("""
        This system uses 26 different algorithms to find the optimal plate ratio.
        Each algorithm uses different optimization techniques.
        """)
    
    # Main content area
    if input_method == "Manual Entry":
        st.markdown("### 📦 Manual Item Entry")
        n_items = st.number_input("Number of Items", min_value=1, max_value=500, value=1)
        
        # Create input fields
        data = []
        cols = st.columns([0.5, 2, 2, 2, 2])
        cols[0].markdown("**SL**")
        cols[1].markdown("**Style**")
        cols[2].markdown("**Color**")
        cols[3].markdown("**Size**")
        cols[4].markdown("**Quantity**")
        
        for i in range(n_items):
            cols = st.columns([0.5, 2, 2, 2, 2])
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
        uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
        
        if uploaded_file:
            df = pd.read_excel(uploaded_file)
            st.dataframe(df, use_container_width=True)
            data = df.to_dict('records')
    
    # Generate button
    if st.button("🚀 Generate Plans", type="primary", use_container_width=True):
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
            tag = item.get("Style", f"Item {item['SL']}")
            qty = item.get("Quantity", 0)
            if qty > 0:
                demand[tag] = int(qty * (1 + addon_percent / 100))
                original_qty[tag] = int(qty)
                styles_dict[tag] = item.get("Style", "")
                colors_dict[tag] = item.get("Color", "")
                sizes_dict[tag] = item.get("Size", "")
        
        if not demand:
            st.error("⚠️ No valid data found!")
            return
        
        # Run all algorithms
        with st.spinner("🔍 Running all 26 algorithms..."):
            results = {}
            progress_bar = st.progress(0)
            
            for idx, (algo_name, _) in enumerate(ALGORITHM_REGISTRY.items()):
                try:
                    optimizer = get_algorithm(algo_name, demand, capacity, max_plates)
                    plates = optimizer.optimize()
                    results[algo_name] = plates
                except Exception as e:
                    st.warning(f"⚠️ {algo_name} failed: {str(e)}")
                    # Use V3 as fallback
                    optimizer = get_algorithm("V3 - Smart Decimal Balancing", demand, capacity, max_plates)
                    results[algo_name] = optimizer.optimize()
                
                progress_bar.progress((idx + 1) / len(ALGORITHM_REGISTRY))
            
            progress_bar.empty()
        
        # Find best algorithm
        best_algo = None
        best_waste = float('inf')
        best_plates = None
        
        for algo_name, plates in results.items():
            if plates:
                waste = calculate_waste_percent(plates, demand)
                if waste < best_waste:
                    best_waste = waste
                    best_algo = algo_name
                    best_plates = plates
        
        # Display results
        if best_plates:
            st.success(f"🏆 Best Algorithm: **{best_algo}** | Waste: **{best_waste}%**")
            
            # Create summary
            from utils.helpers import build_full_summary
            summary_df = build_full_summary(best_plates, demand, original_qty)
            st.dataframe(summary_df, use_container_width=True)
            
            # Download buttons
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


if __name__ == "__main__":
    main()
