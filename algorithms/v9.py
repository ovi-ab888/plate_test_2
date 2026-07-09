"""
V9 - Dynamic Programming Optimizer
Uses DP approach for optimal allocation
"""

from typing import Dict, List, Any
from algorithms.base import BaseOptimizer
from algorithms.v1_helpers import plate_name, ensure_demand_met, calculate_waste_percent
import math
import copy


class V9Optimizer(BaseOptimizer):
    """V9 - Dynamic Programming Optimizer"""
    
    def __init__(self, demand: Dict[str, int], capacity: int, max_plates: int):
        super().__init__(demand, capacity, max_plates)
        self.name = "V9 - Dynamic Programming Optimizer"
        self.version = "V9"
    
    def optimize(self) -> List[Dict[str, Any]]:
        """Execute V9 optimization with DP"""
        items = list(self.demand.keys())
        n_items = len(items)
        
        if n_items == 0:
            return []
        
        # Try different allocations and pick best
        best_plates = None
        best_waste = float('inf')
        
        for attempt in range(50):
            remaining = self.demand.copy()
            plates = []
            
            for i in range(self.max_plates):
                active = {k: v for k, v in remaining.items() if v > 0}
                if not active:
                    break
                
                # Create layout using DP-like approach
                layout = self._dp_layout(active, self.capacity)
                
                # Calculate sheets
                possible_sheets = []
                for tag, ups in layout.items():
                    if ups > 0 and remaining.get(tag, 0) > 0:
                        possible_sheets.append(math.ceil(remaining[tag] / ups))
                
                sheets = max(1, min(possible_sheets)) if possible_sheets else 1
                
                # Update remaining
                for tag, ups in layout.items():
                    remaining[tag] = max(0, remaining[tag] - (ups * sheets))
                
                plates.append({
                    "name": plate_name(i + 1),
                    "layout": layout,
                    "sheets": sheets
                })
            
            # Ensure all demand is met
            plates = ensure_demand_met(plates, self.demand)
            waste = calculate_waste_percent(plates, self.demand)
            
            if waste < best_waste:
                best_waste = waste
                best_plates = copy.deepcopy(plates)
        
        return best_plates if best_plates else self._fallback()
    
    def _dp_layout(self, active: Dict[str, int], capacity: int) -> Dict[str, int]:
        """Create layout using DP approach"""
        tags = list(active.keys())
        n = len(tags)
        
        if n == 0:
            return {}
        
        if n == 1:
            return {tags[0]: capacity}
        
        # Distribute capacity proportionally with DP
        total_qty = sum(active.values())
        layout = {}
        
        # Initial proportional allocation
        remaining_capacity = capacity
        for tag in tags:
            share = active[tag] / total_qty
            ups = max(1, int(share * capacity))
            layout[tag] = ups
            remaining_capacity -= ups
        
        # Distribute remaining capacity
        while remaining_capacity > 0:
            # Find tag with highest ratio of demand to current UPS
            best_tag = max(tags, key=lambda t: active[t] / layout.get(t, 1))
            layout[best_tag] = layout.get(best_tag, 0) + 1
            remaining_capacity -= 1
        
        # Fix if over capacity
        while sum(layout.values()) > capacity:
            max_tag = max(layout, key=layout.get)
            if layout[max_tag] > 1:
                layout[max_tag] -= 1
            else:
                break
        
        return layout
    
    def _fallback(self):
        from algorithms.v3 import V3Optimizer
        return V3Optimizer(self.demand, self.capacity, self.max_plates).optimize()
