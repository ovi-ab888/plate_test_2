"""
Item Entry Module - Manual Entry & Excel Upload (Dynamic Column Support)
"""
import math
import pandas as pd
import streamlit as st

# Keywords used to auto-detect the Quantity column
QTY_KEYWORDS = ['quantity', 'qty', 'qty.', 'quantities', 'total', 'pcs', 'pieces', 'count']


def render_manual_entry(n_items):
    """Renders manual entry rows and returns list of item dicts"""
    data = []
    item_meta = {}
    meta_columns = ["Style", "Color", "Size"]

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
            style_val = style or f"Item {i+1}"
            data.append({
                "SL": i+1,
                "Style": style_val,
                "Color": color or "N/A",
                "Size": size or "N/A",
                "Quantity": qty
            })
            item_meta[style_val] = {
                "Style": style_val,
                "Color": color or "N/A",
                "Size": size or "N/A"
            }

    st.session_state['item_meta'] = item_meta
    st.session_state['item_meta_columns'] = meta_columns

    return data


def render_excel_upload(addon_percent):
    """
    Renders Excel upload UI, auto-detects the Quantity column,
    treats ALL other columns as dynamic metadata (original name + order preserved).
    Returns (original_qty, demand) dicts, or calls st.stop() if not ready.
    """
    st.markdown('<div class="card"><div class="card-title" style="text-align: center; display: block; width: 100%;">📂 Upload Excel File</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Excel file with Item Details",
        type=["xlsx", "xls"],
        help="Quantity column auto-detect hobe. Baki column (jekono naam) shoja report-e chole jabe."
    )

    if uploaded_file is None:
        st.info("📤 Please upload an Excel file to continue.")
        st.stop()

    try:
        df = pd.read_excel(uploaded_file)
        df = df.dropna(how='all')

        if df.empty or len(df.columns) == 0:
            st.error("❌ File-e kono valid data pawa jayni.")
            st.stop()

        # ================================================================
        # STEP 1: Auto-detect Quantity column (keyword match)
        # ================================================================
        qty_col = None
        for col in df.columns:
            col_lower = str(col).lower().strip()
            if col_lower in QTY_KEYWORDS:
                qty_col = col
                break

        # Fallback: first numeric column
        if qty_col is None:
            for col in df.columns:
                if df[col].dtype in ['int64', 'float64']:
                    qty_col = col
                    break

        # Fallback: last column
        if qty_col is None:
            qty_col = df.columns[-1]

        if qty_col is None:
            st.error("❌ Could not find 'Quantity' column. Please ensure your file has a quantity column.")
            st.info("📌 Column names can be: 'Quantity', 'Qty', 'QTY', 'Total', 'Pcs'")
            st.stop()

        # ================================================================
        # STEP 2: Baki shob column = dynamic meta column (original order-e)
        # ================================================================
        meta_cols = [c for c in df.columns if c != qty_col]
        # Pandas auto-generate kora "Unnamed: N" (blank header) column bad dao
        meta_cols = [c for c in meta_cols if not str(c).lower().strip().startswith('unnamed')]

        # ================================================================
        # STEP 3: Row by row process
        # ================================================================
        item_meta = {}
        tags = []
        qty_list = []
        preview_rows = []
        skipped_rows = 0

        for idx, row in df.iterrows():
            raw_qty = row[qty_col]

            if pd.isna(raw_qty):
                skipped_rows += 1
                continue

            try:
                qty_int = int(float(raw_qty))
            except (ValueError, TypeError):
                skipped_rows += 1
                continue

            if qty_int <= 0:
                skipped_rows += 1
                continue

            tag = f"Item {len(tags) + 1}"

            meta = {}
            preview_row = {}
        for col in meta_cols:
            val = row[col]
            if pd.isna(val):
                val_str = ""
            elif isinstance(val, float) and val.is_integer():
                # 7120044.0 -> "7120044" (.0 bad dao)
                val_str = str(int(val))
            else:
                val_str = str(val).strip()
            meta[str(col)] = val_str
            preview_row[str(col)] = val_str

            preview_row["Quantity"] = qty_int

            tags.append(tag)
            qty_list.append(qty_int)
            item_meta[tag] = meta
            preview_rows.append(preview_row)

        if not tags:
            st.error("❌ No valid data found in the file. Please check the format.")
            st.stop()

        preview_df = pd.DataFrame(preview_rows)

        st.success(f"✅ File loaded successfully! {len(tags)} valid items found.")
        if skipped_rows > 0:
            st.warning(f"⚠️ {skipped_rows} rows were skipped (empty or invalid quantity).")

        st.dataframe(preview_df, use_container_width=True)
        st.info(f"📋 Quantity column detected: '{qty_col}' | Other columns: {', '.join(str(c) for c in meta_cols)}")

        # ================================================================
        # STEP 4: Session state-e dynamic meta store
        # ================================================================
        st.session_state['item_meta'] = item_meta
        st.session_state['item_meta_columns'] = [str(c) for c in meta_cols]

        original_qty = {}
        demand = {}
        for t, q in zip(tags, qty_list):
            original_qty[t] = int(q)
            demand[t] = math.ceil(int(q) * (1 + addon_percent / 100))

        st.markdown('</div>', unsafe_allow_html=True)
        return original_qty, demand

    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        st.stop()
