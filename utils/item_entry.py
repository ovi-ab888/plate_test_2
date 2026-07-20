"""
Item Entry Module - Manual Entry & Excel Upload
"""
import math
import pandas as pd
import streamlit as st


def render_manual_entry(n_items):
    """Renders manual entry rows and returns list of item dicts"""
    data = []

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

    return data


def render_excel_upload(addon_percent):
    """
    Renders Excel upload UI, parses file, stores style/color/size in session_state.
    Returns (original_qty, demand) dicts, or (None, None) if not ready (caller should st.stop()).
    """
    st.markdown('<div class="card"><div class="card-title" style="text-align: center; display: block; width: 100%;">📂 Upload Excel File</div>', unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Upload Excel file with Item Details",
        type=["xlsx", "xls"],
        help="File must have columns: SL, Style, Color, Size, Quantity"
    )

    if uploaded_file is None:
        st.info("📤 Please upload an Excel file to continue.")
        st.stop()

    try:
        df = pd.read_excel(uploaded_file)
        df = df.dropna(how='all')

        style_col = color_col = size_col = qty_col = sl_col = None

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
            st.error("❌ Could not find 'Quantity' column. Please ensure your file has a quantity column.")
            st.info("📌 Column names can be: 'Quantity', 'Qty', 'QTY', 'Total'")
            st.stop()

        sl_data = df[sl_col].tolist() if sl_col else list(range(1, len(df) + 1))
        style_data = df[style_col].astype(str).tolist() if style_col else ["N/A"] * len(df)
        color_data = df[color_col].astype(str).tolist() if color_col else ["N/A"] * len(df)
        size_data = df[size_col].astype(str).tolist() if size_col else ["N/A"] * len(df)
        qty_data = df[qty_col].tolist()

        cleaned_data = []
        skipped_rows = 0
        style_list, color_list, size_list, qty_list, sl_list = [], [], [], [], []

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
            st.error("❌ No valid data found in the file. Please check the format.")
            st.stop()

        preview_df = pd.DataFrame({
            "SL": sl_list,
            "Style": style_list,
            "Color": color_list,
            "Size": size_list,
            "Quantity": qty_list
        })

        st.success(f"✅ File loaded successfully! {len(cleaned_data)} valid items found.")
        if skipped_rows > 0:
            st.warning(f"⚠️ {skipped_rows} rows were skipped (empty or invalid data).")

        st.dataframe(preview_df, use_container_width=True)

        detected_cols = []
        if sl_col: detected_cols.append(f"SL = '{sl_col}'")
        if style_col: detected_cols.append(f"Style = '{style_col}'")
        if color_col: detected_cols.append(f"Color = '{color_col}'")
        if size_col: detected_cols.append(f"Size = '{size_col}'")
        if qty_col: detected_cols.append(f"Quantity = '{qty_col}'")
        st.info(f"📋 Detected columns: {', '.join(detected_cols)}")

        n = len(cleaned_data)
        tags = [f"Item {i+1}" for i in range(n)]
        qty = qty_list

        st.session_state['item_styles'] = {f"Item {i+1}": style_list[i] for i in range(n)}
        st.session_state['item_colors'] = {f"Item {i+1}": color_list[i] for i in range(n)}
        st.session_state['item_sizes'] = {f"Item {i+1}": size_list[i] for i in range(n)}

        original_qty = {}
        demand = {}
        for t, q in zip(tags, qty):
            if q > 0:
                original_qty[t] = int(q)
                demand[t] = math.ceil(int(q) * (1 + addon_percent / 100))

        st.markdown('</div>', unsafe_allow_html=True)
        return original_qty, demand

    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        st.stop()
