from typing import Dict, Any

class TaskDetector:
    """
    Deterministically identifies the machine learning task for a specific target column.
    """
    
    @classmethod
    def detect_task(cls, metadata: Dict[str, Any], target_column: str) -> str:
        """
        Returns the detected ML task based on the target column's metadata.
        """
        features = metadata.get("features", {})
        
        if target_column not in features:
            raise ValueError(f"Target column '{target_column}' not found in metadata.")
            
        meta = features[target_column]
        dtype = meta.get("inferred_type", "unknown")
        unique_count = meta.get("unique_count", 0)
        
        if unique_count <= 1:
            raise ValueError(f"Target column '{target_column}' must have more than 1 unique value.")
            
        if dtype in ["integer", "boolean", "categorical", "string"]:
            if unique_count == 2:
                return "Binary Classification"
            elif 2 < unique_count <= 20:
                return "Multi-class Classification"
            elif dtype == "integer" and unique_count > 20:
                return "Regression"
            else:
                # Fallback
                return "Regression" if dtype == "integer" else "Multi-class Classification"
                
        elif dtype in ["float", "numeric", "double"]:
            return "Regression"
            
        return "Regression" # default fallback
