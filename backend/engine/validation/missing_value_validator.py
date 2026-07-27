import pandas as pd
from typing import Dict, Any, List
from backend.engine.profiling.rule_engine import DetectedIssue, RuleSeverity

class MissingValueValidator:
    """
    Detects missing value patterns in the dataset and determines the appropriate severity.
    """
    @staticmethod
    def validate(df: pd.DataFrame) -> List[DetectedIssue]:
        issues = []
        
        missing_counts = df.isna().sum()
        total_rows = len(df)
        
        if total_rows == 0:
            return issues
            
        for col, count in missing_counts.items():
            if count > 0:
                pct = (count / total_rows) * 100
                
                if pct > 30.0:
                    severity = RuleSeverity.CRITICAL
                    desc = f"Column '{col}' has severe missing data ({pct:.1f}%)."
                elif pct > 5.0:
                    severity = RuleSeverity.HIGH
                    desc = f"Column '{col}' has moderate missing data ({pct:.1f}%)."
                else:
                    severity = RuleSeverity.MEDIUM
                    desc = f"Column '{col}' has minor missing data ({pct:.1f}%)."
                    
                issues.append(DetectedIssue(
                    rule_name="MissingDataDetected",
                    description=desc,
                    severity=severity,
                    affected_columns=[col],
                    metric_value=pct
                ))
                
        return issues
