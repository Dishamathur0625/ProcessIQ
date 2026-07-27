from typing import Dict, Any, List
from backend.engine.reports.explainability_report import ExplainabilityReportGenerator
from backend.engine.reports.reproducibility_report import ReproducibilityReportGenerator
from backend.engine.reports.model_readiness_report import ModelReadinessReportGenerator
import pandas as pd

class AnalyticsSummaryReportGenerator:
    """
    Compiles the master summary report combining all aspects of the pipeline execution.
    """
    
    @staticmethod
    def generate(
        executor_result: Dict[str, Any],
        target_variable: str = None
    ) -> str:
        """
        Takes the output dictionary from PipelineExecutor.execute_chain() (or similar orchestration output)
        and formats the master report.
        """
        df_final = executor_result.get("final_dataset", pd.DataFrame())
        lineage = executor_result.get("lineage", [])
        audit = executor_result.get("audit_trail", [])
        features = executor_result.get("feature_metadata", [])
        initial_q = executor_result.get("initial_quality", {})
        final_q = executor_result.get("final_quality", {})
        
        md = ["# ProcessIQ Analytics Summary Report\n"]
        md.append("This is the master summary document for the executed Analytics Engine pipeline.\n")
        
        # 1. Dataset Identity & Quality
        md.append("## 1. Dataset Identity & Quality Metrics\n")
        
        if lineage:
            initial_fingerprint = lineage[0].get("from_version", "Unknown")
            final_fingerprint = lineage[-1].get("to_version", "Unknown")
            md.append(f"- **Initial Fingerprint:** `{initial_fingerprint}`")
            md.append(f"- **Final Fingerprint:** `{final_fingerprint}`\n")
            
        md.append("### Quality Score Deltas (IDRS)")
        
        if initial_q and final_q:
            for k in initial_q.keys():
                init_val = initial_q.get(k, 0)
                final_val = final_q.get(k, 0)
                delta = final_val - init_val
                sign = "+" if delta >= 0 else ""
                md.append(f"- **{k}:** {init_val:.1f}% -> {final_val:.1f}% ({sign}{delta:.1f}%)")
        else:
            md.append("- Quality metrics not available.")
            
        md.append("\n")
        
        # 2. Reproducibility
        md.append(ReproducibilityReportGenerator.generate(
            lineage=lineage,
            audit_trail=audit,
            engine_version="1.0"
        ))
        md.append("\n")
        
        # 3. Explainability
        if features:
            md.append(ExplainabilityReportGenerator.generate(features))
            md.append("\n")
            
        # 4. Model Readiness
        md.append(ModelReadinessReportGenerator.generate(df_final, target_variable))
        
        return "\n".join(md)
