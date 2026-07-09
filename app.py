"""
Plate Ratio System - Complete Edition V1-V26
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime
import math

# Import from algorithms
from algorithms import ALGORITHM_REGISTRY, get_algorithm
from algorithms.v1_helpers import calculate_waste_percent, build_full_summary

st.set_page_config(
    page_title="Plate Ratio System",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
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
    .footer-border {
        text-align: center;
        padding: 2rem;
        margin-top: 3rem;
        border-top: 2px solid #667eea;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>📊 Plate Ratio Intelligence System</h1>
    <p>Complete Edition • 26 Algorithms • Production Ready</p>
    <p style="font-size: 0.85rem; opacity: 0.8;">AI-Powered • Fast • Accurate</p>
    <p style="color: rgba(255,255,255,0.7);">✨ Design by Ovi ✨</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    capacity = st.number_input("Plate Capacity (UPS)", min_value=1, max_value=200, value=10)
    max_plates = st.number_input("Max Plates", min_value=1, max_value=50, value=3)
    addon_percent = st.number_input("Add-on (%)", min_value=0.0, max_value=50.0, value=0.0, step=0.5)
    st.markdown("---")
    st.markdown(f"**Algorithms:** {len(ALGORITHM_REGISTRY)}")
    st.markdown("**V1-V26 Complete**")

# Main content
st.markdown("### 📦 Item Entry")

# Input method
input_method = st.radio(
    "Select Input Method:",
    ["✏️ Manual Entry", "📂 Upload Excel"],
    horizontal=True
)

data = []

if input_method == "✏️ Manual Entry":
    n_items = st.number_input("Number of Items", min_value=1, max_value=500, value=3)
    
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

else:
    uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx", "xls"])
    if uploaded_file:
        try:
            df = pd.read_excel(uploaded_file)
            
            # Auto-detect columns
            qty_col = None
            style_col = None
            
            for col in df.columns:
                col_lower = str(col).lower().strip()
                if col_lower in ['quantity', 'qty', 'total']:
                    qty_col = col
                elif col_lower in ['style', 'styles', 'item']:
                    style_col = col
            
            if qty_col is None and len(df.columns) >= 2:
                qty_col = df.columns[-1]
                style_col = df.columns[0]
            
            if qty_col is None:
                st.error("❌ Could not find 'Quantity' column")
                st.stop()
            
            for idx, row in df.iterrows():
                try:
                    qty = int(float(row[qty_col])) if not pd.isna(row[qty_col]) else 0
                    if qty > 0:
                        style = str(row[style_col]) if style_col and not pd.isna(row[style_col]) else f"Item {idx+1}"
                        data.append({
                            "SL": idx+1,
                            "Style": style,
                            "Color": "N/A",
                            "Size": "N/A",
                            "Quantity": qty
                        })
                except:
                    continue
            
            if data:
                st.success(f"✅ Loaded {len(data)} items!")
                st.dataframe(pd.DataFrame(data), use_container_width=True)
            else:
                st.warning("⚠️ No valid data found")
                
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Generate button
if st.button("🚀 Generate Plans", type="primary", use_container_width=True):
    if not data:
        st.error("⚠️ Please enter at least one item with quantity > 0")
    else:
        # Process data
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
            # Run all algorithms
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
                    except Exception as e:
                        # Silently skip failed algorithms
                        pass
                    
                    progress_bar.progress((idx + 1) / len(algo_list))
                
                progress_bar.empty()
                status_text.empty()
            
            if not results:
                st.error("❌ No algorithm succeeded!")
            else:
                # Compare results
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
                
                # Find best
                best_algo = comparison_df.iloc[0]["Algorithm"]
                best_waste = comparison_df.iloc[0]["Waste %"]
                best_plates = results[best_algo]
                
                # Show best
                st.markdown(f"""
                <div class="best-algo">
                    <h2>🏆 BEST ALGORITHM: {best_algo}</h2>
                    <p style="font-size: 1.5rem; margin: 0.5rem 0;">Waste: {best_waste}%</p>
                    <p style="margin: 0;">Total Algorithms Tested: {len(results)}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Show comparison (without matplotlib)
                with st.expander("📊 All Algorithms Comparison", expanded=False):
                    st.dataframe(comparison_df, use_container_width=True)
                
                # Show best report
                st.markdown("---")
                st.markdown("## 📋 Best Algorithm Report")
                
                summary_df = build_full_summary(best_plates, demand, original_qty)
                st.dataframe(summary_df, use_container_width=True, height=300)
                
                # Plate details
                st.markdown("### 🧾 Plate Details")
                plate_rows = []
                for idx, p in enumerate(best_plates, 1):
                    plate_rows.append({
                        "SL": idx,
                        "Plate ID": p.get("name", f"Plate {idx}"),
                        "Sheets": p.get("sheets", 0),
                        "Layout": ", ".join([f"{k}:{v}" for k, v in p["layout"].items()])
                    })
                st.dataframe(pd.DataFrame(plate_rows), use_container_width=True)

# Footer
st.markdown("""
<div class="footer-border">
    <p style="margin: 0; font-size: 0.85rem; color: #666;">
        © 2025 Plate Ratio System | Version 26 (Complete Edition)
    </p>
    <p style="margin: 8px 0; font-size: 0.8rem; color: #888;">
        26 Algorithms • Production Ready • AI-Powered
    </p>
    <p style="color: #667eea; font-size: 0.85rem; font-weight: 600; margin: 10px 0 0 0;">
        ✨ Developed by Ovi | All Rights Reserved ✨
    </p>
</div>
""", unsafe_allow_html=True)
