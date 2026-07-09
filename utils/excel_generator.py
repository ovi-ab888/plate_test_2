"""
Excel Report Generator
"""

from io import BytesIO
import pandas as pd
from typing import Dict, List, Any
from .helpers import build_full_summary


def generate_excel_report(plates: List[Dict[str, Any]], demand: Dict[str, int],
                          original_qty: Dict[str, int], algo_name: str,
                          waste_percent: float) -> BytesIO:
    """Generate Excel report"""
    
    bio = BytesIO()
    
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        # Summary sheet
        summary_df = build_full_summary(plates, demand, original_qty)
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        
        # Plate details
        plate_rows = []
        for idx, p in enumerate(plates, 1):
            plate_rows.append({
                "SL": idx,
                "Plate ID": p.get("name", f"Plate {idx}"),
                "Sheets Required": p.get("sheets", 0),
                "Total UPS": sum(p["layout"].values()),
                "Layout": ", ".join([f"{k}:{v}" for k, v in p["layout"].items()])
            })
        
        plate_df = pd.DataFrame(plate_rows)
        plate_df.to_excel(writer, sheet_name="Plate Details", index=False)
        
        # Algorithm info
        info_df = pd.DataFrame({
            "Property": ["Algorithm", "Waste %", "Total Plates", "Total Sheets"],
            "Value": [
                algo_name,
                waste_percent,
                len(plates),
                sum(p.get("sheets", 0) for p in plates)
            ]
        })
        info_df.to_excel(writer, sheet_name="Info", index=False)
    
    bio.seek(0)
    return bio
