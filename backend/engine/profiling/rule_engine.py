from enum import Enum
from typing import Dict, Any, List
from pydantic import BaseModel

class RuleSeverity(str, Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"
    INFO = "Info"

class DetectedIssue(BaseModel):
    rule_name: str
    description: str
    severity: RuleSeverity
    affected_columns: List[str] = []
    metric_value: Any = None

class RuleEngine:
    """
    Evaluates dataset metrics against deterministic industrial thresholds.
    Assigns severities to guide the Recommendation Engine.
    """
    
    @staticmethod
    def evaluate(metrics: Dict[str, Any]) -> List[DetectedIssue]:
        issues = []
        
        # 1. Missing Values Rules
        missing = metrics.get("missing", {})
        total_missing = missing.get("total_missing_percentage", 0.0)
        
        if total_missing > 30.0:
            issues.append(DetectedIssue(
                rule_name="SevereMissingData",
                description=f"Dataset has {total_missing:.1f}% missing data.",
                severity=RuleSeverity.CRITICAL,
                metric_value=total_missing
            ))
        elif total_missing > 5.0:
            issues.append(DetectedIssue(
                rule_name="ModerateMissingData",
                description=f"Dataset has {total_missing:.1f}% missing data.",
                severity=RuleSeverity.HIGH,
                metric_value=total_missing
            ))
        elif total_missing > 0.0:
            issues.append(DetectedIssue(
                rule_name="MinorMissingData",
                description=f"Dataset has {total_missing:.1f}% missing data.",
                severity=RuleSeverity.LOW,
                metric_value=total_missing
            ))
            
        # 2. Duplicate Rows Rules
        duplicate_pct = metrics.get("duplicate_percentage", 0.0)
        if duplicate_pct > 10.0:
            issues.append(DetectedIssue(
                rule_name="SevereDuplicates",
                description=f"Dataset contains {duplicate_pct:.1f}% exact duplicate rows.",
                severity=RuleSeverity.HIGH,
                metric_value=duplicate_pct
            ))
        elif duplicate_pct > 0.0:
            issues.append(DetectedIssue(
                rule_name="MinorDuplicates",
                description=f"Dataset contains {duplicate_pct:.1f}% exact duplicate rows.",
                severity=RuleSeverity.MEDIUM,
                metric_value=duplicate_pct
            ))
            
        # Add future rules for Skew, Outliers, etc. here
            
        return issues
