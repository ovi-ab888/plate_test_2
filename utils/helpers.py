"""
Common helper functions used across all algorithms
"""

import string
import math
from typing import Dict, List, Any


def plate_name(n: int) -> str:
    """Convert number to Excel-style column name (A, B, C, ..., Z, AA, AB, ...)"""
    n -= 1
    chars = string.ascii_uppercase
    out = ""
    while True:
        out = chars[n % 26] + out
        n = n // 26 - 1
        if n < 0:
            break
    return out


def create_valid_layout(active: Dict[str, int], capacity: int, method: str = "balanced") -> Dict[str, int]:
    """
    Create a layout that respects capacity even when items > capacity
    Methods: "balanced", "proportional", "greedy"
    """
    if not active:
        return {}
    
    total_qty = sum(active.values())
    n_items = len(active)
    
    # Special case: more items than capacity
    if n_items > capacity:
        layout = {}
        
        if method == "balanced":
            # Proportional UPS for each item
            for tag, qty in active.items():
                ups = max(1, int((qty / total_qty) * capacity))
                layout[tag] = ups
            
            # Exact capacity enforce
            while sum(layout.values()) > capacity:
                max_tag = max(layout, key=layout.get)
                if layout[max_tag] > 1:
                    layout[max_tag] -= 1
                else:
                    min_tag = min(active, key=lambda t: active[t])
                    if layout.get(min_tag, 0) > 0:
                        layout[min_tag] = 0
                    else:
                        break
            
            while sum(layout.values()) < capacity:
                max_tag = max(active, key=lambda t: active[t] / (layout.get(t, 1) + 1))
                layout[max_tag] = layout.get(max_tag, 0) + 1
            
            return layout
        
        elif method == "greedy":
            # Give 1 to each item, then fill remaining capacity
            for tag in active.keys():
                layout[tag] = 1
            
            remaining_cap = capacity - sum(layout.values())
            
            if remaining_cap > 0:
                sorted_items = sorted(active.items(), key=lambda x: x[1], reverse=True)
                for tag, _ in sorted_items:
                    if remaining_cap <= 0:
                        break
                    layout[tag] = layout.get(tag, 1) + 1
                    remaining_cap -= 1
            
            return layout
        
        elif method == "proportional":
            # Proportional distribution
            for tag, qty in active.items():
                ups = int((qty / total_qty) * capacity)
                if ups < 1:
                    ups = 1 if len(active) <= capacity else 0
                layout[tag] = ups
            
            # Exact capacity enforce
            while sum(layout.values()) > capacity:
                max_tag = max(layout, key=layout.get)
                if layout[max_tag] > 1:
                    layout[max_tag] -= 1
                else:
                    break
            
            while sum(layout.values()) < capacity:
                max_tag = max(active, key=lambda t: active[t] / (layout.get(t, 1) + 1))
                layout[max_tag] = layout.get(max_tag, 0) + 1
            
            return layout
    
    # Normal case: items <= capacity
    layout = {}
    
    if method == "balanced":
        for tag, qty in active.items():
            ideal = (qty / total_qty) * capacity
            base = int(ideal)
            if base < 1:
                base = 1
            layout[tag] = base
        
        # Adjust to exact capacity
        while sum(layout.values()) > capacity:
            max_tag = max(layout, key=layout.get)
            if layout[max_tag] > 1:
                layout[max_tag] -= 1
            else:
                break
        
        while sum(layout.values()) < capacity:
            fractional = {}
            for tag, qty in active.items():
                ideal = (qty / total_qty) * capacity
                fractional[tag] = ideal - int(ideal)
            best = max(fractional, key=fractional.get)
            layout[best] = layout.get(best, 0) + 1
    
    else:  # proportional or greedy
        for tag, qty in active.items():
            ups = max(1, int((qty / total_qty) * capacity))
            layout[tag] = ups
        
        while sum(layout.values()) > capacity:
            max_tag = max(layout, key=layout.get)
            if layout[max_tag] > 1:
                layout[max_tag] -= 1
            else:
                break
        
        while sum(layout.values()) < capacity:
            max_tag = max(active, key=lambda t: active[t] / (layout.get(t, 1) + 1))
            layout[max_tag] = layout.get(max_tag, 0) + 1
    
    return layout


def ensure_demand_met(plates: List[Dict[str, Any]], demand: Dict[str, int]) -> List[Dict[str, Any]]:
    """Ensure all demand is met - no negative excess"""
    if not plates:
        return plates
    
    for tag in demand.keys():
        total_produced = 0
        for plate in plates:
            total_produced += plate["layout"].get(tag, 0) * plate["sheets"]
        
        if total_produced < demand.get(tag, 0):
            shortfall = demand.get(tag, 0) - total_produced
            if plates:
                last_plate = plates[-1]
                ups = last_plate["layout"].get(tag, 1)
                additional_sheets = math.ceil(shortfall / max(1, ups))
                last_plate["sheets"] += additional_sheets
    
    # Ensure all plates have names
    for idx, plate in enumerate(plates):
        if "name" not in plate:
            plate["name"] = plate_name(idx + 1)
    
    return plates
