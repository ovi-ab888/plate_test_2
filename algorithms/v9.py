"""
High-Efficiency Multi-Phase Dynamic Chunking Engine for extreme variance
"""

from typing import Dict, List, Any
from algorithms.base import BaseOptimizer
from algorithms.v1_helpers import plate_name, ensure_demand_met, calculate_waste_percent
import math
import copy


def algo_smart_clustering_optimizer(demand: dict, capacity: int, max_plates: int) -> list:
    """V9 - High-Efficiency Multi-Phase Dynamic Chunking Engine for extreme variance"""
    if not demand: return []
    
    remaining = copy.deepcopy(demand)
    plates = []
    
    for p_idx in range(max_plates):
        active = {k: v for k, v in remaining.items() if v > 0}
        if not active: break
        
        sorted_active = sorted(active.items(), key=lambda x: x[1], reverse=True)
        total_active_qty = sum(active.values())
        
        layout = {}
        for tag, qty in sorted_active:
            share = qty / total_active_qty
            allocated_ups = int(round(share * capacity))
            if qty > 0 and allocated_ups < 1:
                allocated_ups = 0
            layout[tag] = allocated_ups
            
        while sum(layout.values()) > capacity:
            max_tag = max(layout, key=lambda k: (layout[k], remaining[k]))
            if layout[max_tag] > 0: layout[max_tag] -= 1
            else: break
            
        while sum(layout.values()) < capacity:
            max_pressure_tag = max(active.keys(), key=lambda k: remaining[k] / (layout.get(k, 0) + 1))
            layout[max_pressure_tag] = layout.get(max_pressure_tag, 0) + 1
            
        valid_sheets = []
        for tag, ups in layout.items():
            if ups > 0:
                valid_sheets.append(ceil(remaining[tag] / ups))
                
        if not valid_sheets: break
        valid_sheets.sort()
        
        target_idx = min(int(len(valid_sheets) * 0.25), len(valid_sheets) - 1)
        sheets = max(1, valid_sheets[target_idx])
        
        for tag, ups in layout.items():
            if ups > 0: remaining[tag] = max(0, remaining[tag] - (ups * sheets))
            
        plates.append({
            "name": plate_name(p_idx + 1),
            "layout": layout,
            "sheets": sheets,
            "plate_index": p_idx + 1
        })
        
    return ensure_demand_met(plates, demand)

    
    def _fallback(self):
        from algorithms.v3 import V3Optimizer
        return V3Optimizer(self.demand, self.capacity, self.max_plates).optimize()
