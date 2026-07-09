"""
V1 - Plate Ratio System (Basic Version)
"""

from typing import Dict, List, Any
from algorithms.base import BaseOptimizer
import math


def plate_name(n: int) -> str:
    """Convert number to Excel-style column name"""
    import string
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
    """Create a layout that respects capacity"""
    if not active:
        return {}
    
    total_qty = sum(active.values())
    n_items = len(active)
    
    if n_items > capacity:
        layout = {}
        
        if method == "balanced":
            for tag, qty in active.items():
                ups = max(1, int((qty / total_qty) * capacity))
                layout[tag] = ups
            
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
            for tag, qty in active.items():
                ups = int((qty / total_qty) * capacity)
                if ups < 1:
                    ups = 1 if len(active) <= capacity else 0
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
    
    layout = {}
    
    if method == "balanced":
        for tag, qty in active.items():
            ideal = (qty / total_qty) * capacity
            base = int(ideal)
            if base < 1:
                base = 1
            layout[tag] = base
        
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
    
    else:
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
    """Ensure all demand is met"""
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
    
    for idx, plate in enumerate(plates):
        if "name" not in plate:
            plate["name"] = plate_name(idx + 1)
    
    return plates


class V1Optimizer(BaseOptimizer):
    """V1 - Basic Plate Ratio System"""
    
    def __init__(self, demand: Dict[str, int], capacity: int, max_plates: int):
        super().__init__(demand, capacity, max_plates)
        self.name = "V1 - Plate Ratio System"
        self.version = "V1"
    
    def optimize(self) -> List[Dict[str, Any]]:
        """Execute V1 optimization"""
        remaining = self.demand.copy()
        plates = []
        
        for i in range(self.max_plates):
            active = {k: v for k, v in remaining.items() if v > 0}
            if not active:
                break
            
            layout = create_valid_layout(active, self.capacity, "balanced")
            
            possible_sheets = []
            for tag, ups in layout.items():
                if ups > 0 and remaining.get(tag, 0) > 0:
                    possible_sheets.append(math.ceil(remaining[tag] / ups))
            
            sheets = max(1, min(possible_sheets)) if possible_sheets else 1
            
            for tag, ups in layout.items():
                remaining[tag] = max(0, remaining[tag] - (ups * sheets))
            
            plates.append({
                "name": plate_name(i + 1),
                "layout": layout,
                "sheets": sheets
            })
        
        return ensure_demand_met(plates, self.demand)
