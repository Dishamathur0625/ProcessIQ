from typing import List, Dict, Any
from backend.schemas.metrics import IDRSReport

def evaluate_rules(report: IDRSReport) -> List[Dict[str, Any]]:
    """
    Deterministic rule engine that sits BEFORE the LLM.
    Generates hard rules and recommendations based on the IDRS report.
    The LLM simply explains these rules, preventing hallucination.
    """
    recommendations = []
    
    if report.missing_ratio > 0.5:
        recommendations.append({
            "issue": f"Critical missing values ({report.missing_ratio*100:.1f}%)",
            "action": "drop_column",
            "confidence": 98,
            "reason": "Missing ratio exceeds 50%; imputation is unreliable."
        })
    elif report.missing_ratio > 0:
        recommendations.append({
            "issue": f"Moderate missing values ({report.missing_ratio*100:.1f}%)",
            "action": "median_imputation",
            "confidence": 85,
            "reason": "Missing values present; median imputation is robust for skewed industrial data."
        })
        
    if report.outlier_ratio > 0.05:
        recommendations.append({
            "issue": f"High outlier presence ({report.outlier_ratio*100:.1f}%)",
            "action": "isolation_forest_outliers",
            "confidence": 92,
            "reason": "Outliers exceed 5%; recommend anomaly detection to flag noisy sensor readings."
        })
        
    if report.duplicate_ratio > 0:
        recommendations.append({
            "issue": f"Duplicate rows detected ({report.duplicate_ratio*100:.1f}%)",
            "action": "drop_duplicates",
            "confidence": 100,
            "reason": "Duplicates artificially inflate model confidence and should be removed."
        })
        
    return recommendations
