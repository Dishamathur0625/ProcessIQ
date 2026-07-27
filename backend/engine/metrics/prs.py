import pandas as pd
from backend.schemas.metrics import PRSReport

def calculate_prs(df: pd.DataFrame, target_column: str, task_type: str = "regression") -> PRSReport:
    """
    Calculates the Prediction Readiness Score (PRS) for a given target.
    """
    if target_column not in df.columns:
        return PRSReport(
            overall_score=0.0,
            task_type=task_type,
            target_exists=False,
            sufficient_samples=len(df) > 50,
            feature_variance_score=0.0,
            ready_for_ml=False
        )
        
    score = 100.0
    sufficient_samples = len(df) > 100
    if not sufficient_samples:
        score -= 40
        
    # Check feature variance
    numeric_features = df.drop(columns=[target_column]).select_dtypes(include='number')
    if numeric_features.empty:
        feature_variance_score = 0.0
        score -= 50
    else:
        variances = numeric_features.var()
        zero_variance_cols = (variances == 0).sum()
        feature_variance_score = 100.0 - (zero_variance_cols / len(numeric_features.columns) * 100)
        score -= (100.0 - feature_variance_score) * 0.5
        
    ready = score >= 60.0
    
    return PRSReport(
        overall_score=max(0.0, min(100.0, score)),
        task_type=task_type,
        target_exists=True,
        sufficient_samples=sufficient_samples,
        feature_variance_score=feature_variance_score,
        ready_for_ml=ready
    )
