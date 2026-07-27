import pandas as pd
from typing import Dict, Any

class MetricsEngine:
    """
    Centralized hub for calculating all data quality and statistical metrics.
    Ensures absolute consistency across the Profiler, Preprocessors, and Reports.
    """
    
    @staticmethod
    def calculate_missing(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates exact missing value counts and percentages per column."""
        if df.empty:
            return {"total_missing": 0, "total_missing_percentage": 0.0, "columns": {}}
            
        missing_counts = df.isna().sum()
        missing_pcts = (missing_counts / len(df)) * 100
        
        return {
            "total_missing": int(missing_counts.sum()),
            "total_missing_percentage": float(missing_counts.sum() / df.size) * 100,
            "columns": {
                col: {"count": int(missing_counts[col]), "percentage": float(missing_pcts[col])}
                for col in df.columns if missing_counts[col] > 0
            }
        }
        
    @staticmethod
    def calculate_outliers(df: pd.DataFrame) -> Dict[str, Any]:
        """Calculates basic IQR-based outlier estimations per numeric column."""
        numeric_df = df.select_dtypes(include='number')
        if numeric_df.empty:
            return {}
            
        Q1 = numeric_df.quantile(0.25)
        Q3 = numeric_df.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = ((numeric_df < lower_bound) | (numeric_df > upper_bound)).sum()
        
        return {
            col: int(outliers[col]) for col in numeric_df.columns if outliers[col] > 0
        }
        
    @staticmethod
    def calculate_skew(df: pd.DataFrame) -> Dict[str, float]:
        numeric_df = df.select_dtypes(include='number')
        if numeric_df.empty:
            return {}
        return numeric_df.skew().to_dict()
        
    @staticmethod
    def calculate_idrs(metrics: Dict[str, Any]) -> float:
        """
        Calculates the Industrial Dataset Readiness Score (IDRS).
        A central metric reflecting overall dataset quality.
        """
        score = 100.0
        
        missing = metrics.get('missing', {}).get('total_missing_percentage', 0.0)
        score -= min(30.0, missing * 1.5) # Heavy penalty for missing
        
        # Additional penalties would be calculated here based on outliers, skew, etc.
        
        return max(0.0, min(100.0, score))
