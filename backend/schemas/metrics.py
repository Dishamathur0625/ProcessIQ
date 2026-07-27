from pydantic import BaseModel
from typing import List, Optional

class IDRSReport(BaseModel):
    """
    Industrial Dataset Readiness Score
    """
    overall_score: float
    missing_ratio: float
    outlier_ratio: float
    duplicate_ratio: float
    sampling_consistency: float
    feature_correlation_penalty: float
    leakage_penalty: float

class PRSReport(BaseModel):
    """
    Prediction Readiness Score
    """
    overall_score: float
    task_type: str
    target_exists: bool
    sufficient_samples: bool
    feature_variance_score: float
    class_balance_score: Optional[float] = None
    time_consistency_score: Optional[float] = None
    ready_for_ml: bool
