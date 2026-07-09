"""
Algorithms Package - Start with V3 only
"""

# Only import V3 for testing
from algorithms.v3 import V3Optimizer

# Registry with only V3
ALGORITHM_REGISTRY = {
    "V3 - Smart Decimal Balancing": V3Optimizer,
}


def get_algorithm(name: str, demand: dict, capacity: int, max_plates: int):
    """Factory function to get algorithm instance"""
    if name not in ALGORITHM_REGISTRY:
        raise ValueError(f"Unknown algorithm: {name}")
    
    optimizer_class = ALGORITHM_REGISTRY[name]
    return optimizer_class(demand, capacity, max_plates)
