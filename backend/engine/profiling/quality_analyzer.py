import pandas as pd
from typing import Dict, Any

class QualityDimensionAnalyzer:
    """
    Computes the 8 core quality dimensions of an industrial dataset.
    Completeness, Consistency, Validity, Uniqueness, Timeliness, Integrity, PRS, and IDRS.
    """
    
    @staticmethod
    def analyze(df: pd.DataFrame, metrics: Dict[str, Any]) -> Dict[str, float]:
        if df.empty:
            return {
                "completeness": 0.0, "consistency": 0.0, "validity": 0.0,
                "uniqueness": 0.0, "timeliness": 0.0, "integrity": 0.0,
                "prediction_readiness": 0.0, "industrial_dataset_readiness": 0.0
            }
            
        # 1. Completeness (Inversely proportional to missing values)
        missing_pct = metrics.get("missing", {}).get("total_missing_percentage", 0.0)
        completeness = max(0.0, 100.0 - (missing_pct * 1.5))
        
        # 2. Uniqueness (Inversely proportional to duplicate rows)
        duplicate_count = df.duplicated().sum()
        duplicate_pct = (duplicate_count / len(df)) * 100 if len(df) > 0 else 0.0
        uniqueness = max(0.0, 100.0 - (duplicate_pct * 2.0))
        
        # 3. Validity (Checking against expected schema/types - placeholder heuristic)
        # Assuming numeric cols without extreme outliers are valid
        validity = 90.0 # Placeholder
        
        # 4. Consistency (Variance/Skew stability - placeholder heuristic)
        consistency = 85.0 # Placeholder
        
        # 5. Timeliness (Checking for gap density in time series - placeholder heuristic)
        timeliness = 80.0 # Placeholder
        
        # 6. Integrity (Foreign key/relational integrity if applicable)
        integrity = 100.0 # Placeholder for flat files
        
        # 7. Prediction Readiness Score (PRS)
        # Heuristic: Complete, Unique, and Consistent datasets are ready for ML
        prs = (completeness * 0.5) + (uniqueness * 0.2) + (consistency * 0.3)
        
        # 8. Industrial Dataset Readiness Score (IDRS)
        # Heuristic: Validity, Timeliness, and Completeness matter most for industrial IoT
        idrs = (completeness * 0.4) + (validity * 0.3) + (timeliness * 0.3)
        
        return {
            "completeness": round(completeness, 2),
            "consistency": round(consistency, 2),
            "validity": round(validity, 2),
            "uniqueness": round(uniqueness, 2),
            "timeliness": round(timeliness, 2),
            "integrity": round(integrity, 2),
            "prediction_readiness": round(prs, 2),
            "industrial_dataset_readiness": round(idrs, 2)
        }
