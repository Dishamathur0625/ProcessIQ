from backend.schemas.automl import AutoMLReport
from typing import Dict, Any

class AutoMLReporter:
    """
    Generates a deterministic markdown report for an AutoML session.
    """
    
    @staticmethod
    def generate_markdown(report: AutoMLReport) -> str:
        md = f"# AutoML Execution Report\n\n"
        md += f"**Session ID:** `{report.session_id}`\n"
        md += f"**Execution Time:** `{report.execution_time_sec:.2f} seconds`\n\n"
        
        md += "## Leaderboard\n\n"
        md += "| Rank | Model | "
        
        if report.leaderboard:
            metrics_keys = list(report.leaderboard[0].metrics.keys())
            md += " | ".join(metrics_keys) + " | Time (s) |\n"
            md += "| " + " | ".join(["---"] * (len(metrics_keys) + 3)) + " |\n"
            
            for i, model in enumerate(report.leaderboard):
                rank = i + 1
                row = f"| {rank} | **{model.model_name}** | "
                for k in metrics_keys:
                    val = model.metrics.get(k, 0)
                    row += f"{val:.4f} | "
                row += f"{model.training_time_sec:.2f} |\n"
                md += row
                
        md += "\n## Best Model Details\n\n"
        if report.leaderboard:
            best = report.leaderboard[0]
            md += f"**Model:** {best.model_name}\n\n"
            md += "### Hyperparameters\n\n```json\n"
            import json
            md += json.dumps(best.hyperparameters, indent=2)
            md += "\n```\n\n"
            
            md += "### Metrics\n\n"
            for k, v in best.metrics.items():
                md += f"- **{k}:** {v:.4f}\n"
                
        md += "\n## Recommendations\n"
        md += f"The {best.model_name if report.leaderboard else 'selected'} model was chosen purely on metric optimization. "
        md += "Review the Explainability artifacts to ensure the model aligns with domain knowledge before deployment.\n"
        
        return md
