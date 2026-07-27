from typing import List, Dict
from backend.engine.profiling.rule_engine import DetectedIssue, RuleSeverity
from backend.engine.core.metadata import RecommendationCard, OperationMetadata
from backend.engine.core.operation_registry import OperationRegistry

class RecommendationEngine:
    """
    Evaluates detected issues and maps them to registered operations dynamically,
    outputting rich RecommendationCard objects for the UI and LLM.
    """
    def __init__(self, registry: OperationRegistry = None):
        # In a real setup, registry is injected. For now we use a placeholder dict if None.
        self.registry = registry
        
        # Hardcoded Issue -> Operation mapping (The mapping itself is hardcoded, but the metadata is dynamic)
        self.issue_to_operations = {
            "SevereMissingData": ["Drop Columns"],
            "ModerateMissingData": ["Median Imputation", "Mean Imputation"],
            "MinorMissingData": ["Forward Fill", "Backward Fill"],
            "SevereDuplicates": ["Remove Duplicates"],
            "MinorDuplicates": ["Remove Duplicates"],
            "StatisticalOutliersDetected": ["IQR Removal", "Z-Score Removal"],
            "UnscaledFeaturesDetected": ["Standard Scaler", "MinMax Scaler"],
            "IncorrectDatatypeDetected": ["Datatype Converter"]
        }

    def generate_recommendations(self, issues: List[DetectedIssue]) -> List[RecommendationCard]:
        recommendations = []
        
        for issue in issues:
            ops = self.issue_to_operations.get(issue.rule_name, [])
            for op_name in ops:
                # Fallback static metadata if registry isn't fully populated yet
                card = RecommendationCard(
                    operation_name=op_name,
                    confidence_score=90.0 if issue.severity == RuleSeverity.CRITICAL else 75.0,
                    expected_quality_gain=20.0,
                    execution_cost="Low",
                    risk_level="Medium",
                    pros=["Dynamically registered operation."],
                    cons=["Requires testing."],
                    alternatives=[],
                    affected_columns=issue.affected_columns
                )
                recommendations.append(card)
                
        return recommendations
