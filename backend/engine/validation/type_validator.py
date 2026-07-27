import pandas as pd
from typing import Dict, Any, List
from backend.engine.profiling.rule_engine import DetectedIssue, RuleSeverity

class TypeValidator:
    """
    Detects numerical columns masquerading as objects/strings, or timestamps stored as strings.
    """
    @staticmethod
    def validate(df: pd.DataFrame) -> List[DetectedIssue]:
        issues = []
        
        if df.empty:
            return issues
            
        object_df = df.select_dtypes(include=['object', 'string'])
        
        for col in object_df.columns:
            # Check if it looks like numeric
            sample = object_df[col].dropna().head(100)
            if sample.empty:
                continue
                
            # Try parsing as numeric
            try_numeric = pd.to_numeric(sample, errors='coerce')
            if try_numeric.notna().sum() > len(sample) * 0.9: # 90% parseable
                issues.append(DetectedIssue(
                    rule_name="IncorrectDatatypeDetected",
                    description=f"Column '{col}' is currently type Object but looks >90% Numeric.",
                    severity=RuleSeverity.MEDIUM,
                    affected_columns=[col],
                    metric_value=float(try_numeric.notna().sum() / len(sample))
                ))
                continue
                
            # Try parsing as datetime
            try_dt = pd.to_datetime(sample, errors='coerce')
            if try_dt.notna().sum() > len(sample) * 0.9: # 90% parseable
                issues.append(DetectedIssue(
                    rule_name="IncorrectDatatypeDetected",
                    description=f"Column '{col}' is currently type Object but looks >90% Datetime.",
                    severity=RuleSeverity.MEDIUM,
                    affected_columns=[col],
                    metric_value=float(try_dt.notna().sum() / len(sample))
                ))
                
        return issues
