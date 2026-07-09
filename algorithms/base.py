"""
Base Optimizer Class - All algorithms inherit from this
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any


class BaseOptimizer(ABC):
    """Base class for all plate ratio optimizers"""
    
    def __init__(self, demand: Dict[str, int], capacity: int, max_plates: int):
        self.demand = demand
        self.capacity = capacity
        self.max_plates = max_plates
        self.name = "Base Optimizer"
        self.version = "V0"
    
    @abstractmethod
    def optimize(self) -> List[Dict[str, Any]]:
        """Main optimization method - must be implemented by child classes"""
        pass
    
    def get_info(self) -> Dict[str, Any]:
        """Return algorithm information"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.__doc__ or "No description available"
        }
