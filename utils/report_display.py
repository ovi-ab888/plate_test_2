"""
Report Display Module - Best Algorithm summary, plate details, Excel/PDF downloads
"""
from datetime import datetime

import pandas as pd
import streamlit as st

from algorithms.v1_helpers import build_full_summary
from utils.pdf_generator import generate_pdf_report, PDF_AVAILABLE
from utils.excel_generator import generate_excel_report, EXCEL_AVAILABLE


def render_report(results, comparison_df, best_algo, best_waste, best_plates, demand, original_qty, job_number):
    """Renders best-algorithm banner, comparison table, summary table, and plate details."""
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


def render_downloads(best_plates, demand, original_qty, best_algo, best_waste, job_number):
    """Renders Excel and PDF download buttons."""
    st.markdown("---")
    st.markdown("## 📥 Download Reports")

    item_meta = st.session_state.get('item_meta', {})
    meta_columns = st.session_state.get('item_meta_columns', [])

    col1, col2 = st.columns(2)

    with col1:
        excel_buffer = generate_excel_report(
            best_plates, demand, original_qty, best_algo, best_waste, job_number,
            item_meta=item_meta, meta_columns=meta_columns
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
        pdf_buffer = generate_pdf_report(
            best_plates, demand, original_qty, best_algo, best_waste, job_number,
            item_meta=item_meta, meta_columns=meta_columns
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

    with col2:
        styles_dict = st.session_state.get('item_styles', {})
        colors_dict = st.session_state.get('item_colors', {})
        sizes_dict = st.session_state.get('item_sizes', {})

        pdf_buffer = generate_pdf_report(
            best_plates, demand, original_qty, best_algo, best_waste, job_number,
            styles_dict, colors_dict, sizes_dict
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
