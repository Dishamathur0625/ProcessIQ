from typing import List, Dict, Any
import re

class TargetDetector:
    """
    Deterministically detects likely target columns for Machine Learning tasks
    based on metadata properties, column names, and cardinality heuristics.
    """
    
    TARGET_KEYWORDS = ["target", "label", "class", "y", "outcome", "result", "price", "status", "is_"]
    
    @classmethod
    def detect_targets(cls, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Takes the feature_metadata artifact (as a dict) and ranks possible targets.
        """
        features = metadata.get("features", {})
        total_rows = metadata.get("row_count", 0)
        
        candidates = []
        
        for col_name, meta in features.items():
            if meta.get("is_identifier", False) or meta.get("is_datetime", False):
                continue
                
            score = 0
            predicted_task = None
            
            # 1. Name match heuristics
            name_lower = col_name.lower()
            for kw in cls.TARGET_KEYWORDS:
                if kw in name_lower:
                    score += 40
                    break
                    
            # 2. Extract properties
            dtype = meta.get("inferred_type", "unknown")
            unique_count = meta.get("unique_count", 0)
            missing_ratio = meta.get("missing_ratio", 0.0)
            
            if missing_ratio > 0.5:
                # Too many missing values to be a good target
                continue
            if unique_count == 1:
                # Constant target is invalid
                continue
                
            # 3. Determine potential task and adjust score
            if dtype in ["integer", "boolean", "categorical", "string"]:
                if unique_count == 2:
                    predicted_task = "Binary Classification"
                    score += 30
                elif 2 < unique_count <= 20:
                    predicted_task = "Multi-class Classification"
                    score += 20
                elif dtype in ["integer", "float"] and unique_count > 20:
                    predicted_task = "Regression"
                    score += 15
                else:
                    # High cardinality string/categorical, likely an ID or text, not target
                    score -= 50
            elif dtype in ["float", "numeric", "double"]:
                predicted_task = "Regression"
                score += 25
                
            if score > 0 and predicted_task:
                # Calculate pseudo-confidence based on score, maxing out at 0.99
                confidence = min(0.99, score / 100.0)
                candidates.append({
                    "column": col_name,
                    "predicted_task": predicted_task,
                    "confidence": round(confidence, 2),
                    "score": score
                })
                
        # Sort by score descending
        candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)
        
        # Remove score from output schema
        for c in candidates:
            del c["score"]
            
        return {"candidates": candidates}
