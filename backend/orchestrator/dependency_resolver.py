from typing import List
from .capability_registry import CAPABILITY_REGISTRY

class DependencyError(Exception):
    """Raised when dependencies cannot be resolved securely."""
    pass

def resolve_dependencies(operations: List[str]) -> List[str]:
    """
    Sorts a list of operations based on their registry requirements and industrial precedence.
    Ensures that foundational cleaning happens before scaling or feature engineering.
    """
    # Strict industrial precedence order
    PRECEDENCE = [
        "drop_duplicates",
        "median_imputation",
        "isolation_forest_outliers",
        "standard_scaler"
    ]
    
    # Validate that all operations are supported in the registry
    for op in operations:
        if op not in CAPABILITY_REGISTRY:
            raise DependencyError(f"Operation '{op}' is not supported in the Capability Registry.")
    
    # Sort the operations based on their index in the precedence list
    sorted_ops = sorted(
        operations, 
        key=lambda op: PRECEDENCE.index(op) if op in PRECEDENCE else 999
    )
    
    return sorted_ops
