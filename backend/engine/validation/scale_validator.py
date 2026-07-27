import pandas as pd
from typing import Dict, Any, List
from backend.engine.profiling.rule_engine import DetectedIssue, RuleSeverity

class ScaleValidator:
    """
    Detects numerical columns with vastly different scales or extreme variances.
    """
    @staticmethod
    def validate(df: pd.DataFrame) -> List[DetectedIssue]:
        issues = []
        numeric_df = df.select_dtypes(include='number')
        
        if numeric_df.empty or len(numeric_df.columns) < 2:
            return issues
            
        ranges = numeric_df.max() - numeric_df.min()
        max_range = ranges.max()
        min_range = ranges[ranges > 0].min() if not ranges[ranges > 0].empty else 1.0
        
        ratio = max_range / min_range
        
        if ratio > 10000:
            severity = RuleSeverity.HIGH
            desc = f"Features have extreme scale differences (Ratio: {ratio:.1f}). Algorithms like KNN or SVM will fail or underperform."
        elif ratio > 100:
            severity = RuleSeverity.MEDIUM
            desc = f"Features have moderate scale differences (Ratio: {ratio:.1f}). Scaling is recommended."
        else:
            return issues # No issue
            
        issues.append(DetectedIssue(
            rule_name="UnscaledFeaturesDetected",
            description=desc,
            severity=severity,
            affected_columns=list(numeric_df.columns),
            metric_value=ratio
        ))
        
        return issues
