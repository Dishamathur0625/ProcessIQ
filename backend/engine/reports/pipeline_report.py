from typing import Dict, Any, List

class PipelineReportGenerator:
    """
    Generates a comprehensive "Before and After" Markdown report following pipeline execution.
    """
    @staticmethod
    def generate_markdown(execution_result: Dict[str, Any]) -> str:
        lines = []
        
        lines.append("# ProcessIQ Pipeline Execution Report\n")
        
        # 1. Quality Improvements
        init_q = execution_result.get("initial_quality", {})
        final_q = execution_result.get("final_quality", {})
        
        lines.append("## Quality Metric Improvements")
        lines.append("| Metric | Before | After | Delta |")
        lines.append("|---|---|---|---|")
        
        for metric in init_q.keys():
            before_val = init_q[metric]
            after_val = final_q.get(metric, before_val)
            delta = after_val - before_val
            trend = "🟢" if delta > 0 else ("🔴" if delta < 0 else "⚪")
            lines.append(f"| **{metric.replace('_', ' ').title()}** | {before_val:.1f} | {after_val:.1f} | {trend} {delta:+.1f} |")
        lines.append("\n")
        
        # 2. Operations Applied
        lines.append("## Operations Applied")
        lineage = execution_result.get("lineage", [])
        for idx, edge in enumerate(lineage, 1):
            lines.append(f"{idx}. **{edge['operation']}**")
            lines.append(f"   - *Audit Hash:* `{edge['audit_hash']}`")
            lines.append(f"   - *Timestamp:* {edge['timestamp']}")
        lines.append("\n")
        
        # 3. Performance Summary
        lines.append("## Performance Summary")
        audit_trail = execution_result.get("audit_trail", [])
        total_time_ms = sum([a["execution_metrics"]["execution_time_ms"] for a in audit_trail])
        total_mem_mb = max([a["execution_metrics"]["memory_usage_mb"] for a in audit_trail]) if audit_trail else 0.0
        
        lines.append(f"- **Total Pipeline Execution Time:** {total_time_ms:.2f} ms")
        lines.append(f"- **Peak Memory Usage:** {total_mem_mb:.2f} MB")
        
        return "\n".join(lines)
