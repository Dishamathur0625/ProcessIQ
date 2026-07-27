from typing import List, Dict, Any
from backend.engine.profiling.rule_engine import DetectedIssue
from backend.engine.core.metadata import RecommendationCard

class ContextBuilder:
    """
    Condenses the raw DatasetProfiler outputs, QualityDimensions, Issues, and Recommendations
    into a structured semantic text block (2-5 KB) optimized for the LLM Copilot.
    """
    
    @staticmethod
    def build_context(
        fingerprint: str,
        quality_scores: Dict[str, float],
        issues: List[DetectedIssue],
        recommendations: List[RecommendationCard]
    ) -> str:
        
        context_lines = []
        
        context_lines.append(f"### Dataset Identity Fingerprint")
        context_lines.append(f"{fingerprint}\n")
        
        context_lines.append("### Quality Dimension Scores (0-100)")
        for dim, score in quality_scores.items():
            context_lines.append(f"- {dim.replace('_', ' ').title()}: {score}")
        context_lines.append("")
        
        context_lines.append("### Critical & High Severity Issues")
        critical_issues = [i for i in issues if i.severity.value in ["Critical", "High"]]
        if not critical_issues:
            context_lines.append("No critical issues detected.")
        for issue in critical_issues:
            context_lines.append(f"- [{issue.severity.value}] {issue.rule_name}: {issue.description}")
        context_lines.append("")
        
        context_lines.append("### Top Operations Recommended (Ranked by Confidence)")
        sorted_recs = sorted(recommendations, key=lambda x: x.confidence_score, reverse=True)
        if not sorted_recs:
            context_lines.append("No operations recommended.")
        for rec in sorted_recs[:5]: # Top 5 only
            context_lines.append(
                f"- {rec.operation_name} (Confidence: {rec.confidence_score}% | "
                f"Expected Quality Gain: +{rec.expected_quality_gain}) | "
                f"Cost: {rec.execution_cost} | Risk: {rec.risk_level}"
            )
            if rec.pros:
                context_lines.append(f"  * Pros: {', '.join(rec.pros)}")
        
        return "\n".join(context_lines)
