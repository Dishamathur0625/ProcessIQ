import pandas as pd
from backend.schemas.metrics import IDRSReport

def calculate_idrs(df: pd.DataFrame) -> IDRSReport:
    """
    Calculates the Industrial Dataset Readiness Score (IDRS).
    """
    total_cells = df.size
    missing_count = df.isna().sum().sum()
    missing_ratio = float(missing_count / total_cells) if total_cells > 0 else 0.0
    
    duplicate_count = df.duplicated().sum()
    duplicate_ratio = float(duplicate_count / len(df)) if len(df) > 0 else 0.0
    
    # Simplistic outlier calculation (e.g. 3 standard deviations)
    # In production, use isolation forest or robust stats
    numeric_df = df.select_dtypes(include='number')
    if not numeric_df.empty:
        z_scores = ((numeric_df - numeric_df.mean()) / numeric_df.std()).abs()
        outliers = (z_scores > 3).sum().sum()
        outlier_ratio = float(outliers / numeric_df.size)
    else:
        outlier_ratio = 0.0
        
    sampling_consistency = 1.0 # placeholder
    feature_correlation_penalty = 0.0 # placeholder
    leakage_penalty = 0.0 # placeholder
    
    # Base score of 100, subtracting penalties
    score = 100.0
    score -= (missing_ratio * 40)
    score -= (duplicate_ratio * 20)
    score -= (outlier_ratio * 20)
    
    score = max(0.0, min(100.0, score))
    
    return IDRSReport(
        overall_score=score,
        missing_ratio=missing_ratio,
        outlier_ratio=outlier_ratio,
        duplicate_ratio=duplicate_ratio,
        sampling_consistency=sampling_consistency,
        feature_correlation_penalty=feature_correlation_penalty,
        leakage_penalty=leakage_penalty
    )
