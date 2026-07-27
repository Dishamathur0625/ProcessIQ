import pandas as pd
from typing import Dict, Any, List
from backend.engine.profiling.rule_engine import DetectedIssue, RuleSeverity

class DuplicateValidator:
    """
    Detects duplicated rows in the dataset and determines the appropriate severity.
    """
    @staticmethod
    def validate(df: pd.DataFrame) -> List[DetectedIssue]:
        issues = []
        
        duplicate_count = df.duplicated().sum()
        total_rows = len(df)
        
        if total_rows == 0 or duplicate_count == 0:
            return issues
            
        pct = (duplicate_count / total_rows) * 100
        
        if pct > 10.0:
            severity = RuleSeverity.HIGH
            desc = f"Dataset contains severe exact duplicate rows ({pct:.1f}%)."
        elif pct > 1.0:
            severity = RuleSeverity.MEDIUM
            desc = f"Dataset contains moderate exact duplicate rows ({pct:.1f}%)."
        else:
            severity = RuleSeverity.LOW
            desc = f"Dataset contains minor exact duplicate rows ({pct:.1f}%)."
            
        issues.append(DetectedIssue(
            rule_name="DuplicateRowsDetected",
            description=desc,
            severity=severity,
            affected_columns=[], # Affects all columns
            metric_value=pct
        ))
        
        return issues
