"""
Algorithms Package - All Plate Ratio Optimizers
"""

# Import all algorithm classes
from algorithms.v1 import V1Optimizer
from algorithms.v2 import V2Optimizer
from algorithms.v3 import V3Optimizer
from algorithms.v4 import V4Optimizer
from algorithms.v5 import V5Optimizer
from algorithms.v6 import V6Optimizer
from algorithms.v7 import V7Optimizer
from algorithms.v8 import V8Optimizer
from algorithms.v11 import V11Optimizer
from algorithms.v12 import V12Optimizer
from algorithms.v15 import V15Optimizer
from algorithms.v16 import V16Optimizer
from algorithms.v17 import V17Optimizer
from algorithms.v18 import V18Optimizer
from algorithms.v19 import V19Optimizer
from algorithms.v20 import V20Optimizer
from algorithms.v21 import V21Optimizer
from algorithms.v22 import V22Optimizer
from algorithms.v24 import V24Optimizer
from algorithms.v25 import V25Optimizer
from algorithms.v26 import V26Optimizer
from algorithms.smart_clustering import SmartClusteringOptimizer

# Registry of all algorithms
ALGORITHM_REGISTRY = {
    "V1 - Plate Ratio System": V1Optimizer,
    "V2 - Common Sheet Optimizer": V2Optimizer,
    "V3 - Smart Decimal Balancing": V3Optimizer,
    "V4 - Multi-Variation Optimizer": V4Optimizer,
    "V5 - AI Mutation Engine": V5Optimizer,
    "V6 - Integer Solver": V6Optimizer,
    "V7 - Simulated Annealing": V7Optimizer,
    "V8 - MCTS Tree Search": V8Optimizer,
    "V11 - Genetic Algorithm": V11Optimizer,
    "V12 - Column Generation": V12Optimizer,
    "V15 - DP Repair Engine": V15Optimizer,
    "V16 - Plate Merge Optimizer": V16Optimizer,
    "V17 - AI Evolution Engine": V17Optimizer,
    "V18 - Global Multi-Plate Optimizer": V18Optimizer,
    "V19 - CP-SAT Optimizer": V19Optimizer,
    "V20 - PSO Optimizer": V20Optimizer,
    "V21 - ACO Optimizer": V21Optimizer,
    "V22 - Q-Learning Optimizer": V22Optimizer,
    "V24 - Differential Evolution": V24Optimizer,
    "V25 - Pareto Optimizer": V25Optimizer,
    "V6 - Smart Clustering": SmartClusteringOptimizer,
    "V26 - NN Predictor": V26Optimizer,
}


def get_algorithm(name: str, demand: dict, capacity: int, max_plates: int):
    """Factory function to get algorithm instance"""
    if name not in ALGORITHM_REGISTRY:
        raise ValueError(f"Unknown algorithm: {name}")
    
    optimizer_class = ALGORITHM_REGISTRY[name]
    return optimizer_class(demand, capacity, max_plates)
