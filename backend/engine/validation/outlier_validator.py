import pandas as pd
from typing import Dict, Any, List
from backend.engine.profiling.rule_engine import DetectedIssue, RuleSeverity

class OutlierValidator:
    """
    Detects statistical outliers in numeric columns using IQR boundaries.
    """
    @staticmethod
    def validate(df: pd.DataFrame) -> List[DetectedIssue]:
        issues = []
        numeric_df = df.select_dtypes(include='number')
        
        if numeric_df.empty:
            return issues
            
        total_rows = len(df)
        
        Q1 = numeric_df.quantile(0.25)
        Q3 = numeric_df.quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outlier_counts = ((numeric_df < lower_bound) | (numeric_df > upper_bound)).sum()
        
        for col, count in outlier_counts.items():
            if count > 0:
                pct = (count / total_rows) * 100
                
                if pct > 15.0:
                    severity = RuleSeverity.HIGH
                    desc = f"Column '{col}' has a severe amount of outliers ({pct:.1f}%)."
                elif pct > 5.0:
                    severity = RuleSeverity.MEDIUM
                    desc = f"Column '{col}' has a moderate amount of outliers ({pct:.1f}%)."
                else:
                    severity = RuleSeverity.LOW
                    desc = f"Column '{col}' has a minor amount of outliers ({pct:.1f}%)."
                    
                issues.append(DetectedIssue(
                    rule_name="StatisticalOutliersDetected",
                    description=desc,
                    severity=severity,
                    affected_columns=[col],
                    metric_value=pct
                ))
                
        return issues
