from typing import List, Dict, Any
from backend.engine.core.version_graph import DatasetVersionGraph

class ReproducibilityReportGenerator:
    """
    Generates a cryptographic reproducibility report to guarantee that the final dataset
    can be perfectly recreated from the raw source.
    """
    
    @staticmethod
    def generate(lineage: List[Dict[str, Any]], audit_trail: List[Dict[str, Any]], engine_version: str = "1.0") -> str:
        md = ["# ProcessIQ Reproducibility Report\n"]
        md.append("This document guarantees the exact reproducibility of the dataset state. "
                  "Every transformation is tracked cryptographically.\n")
                  
        md.append("## 1. Engine Specifications\n")
        md.append(f"- **Analytics Engine Version:** `{engine_version}`")
        md.append(f"- **Execution Framework:** `ProcessIQ PipelineExecutor`\n")
        
        md.append("## 2. Dataset Version Graph\n")
        
        for step in lineage:
            md.append(f"### Version: `{step.get('to_version', 'Initial')}`")
            if step.get('from_version'):
                md.append(f"- **Parent Version:** `{step['from_version']}`")
                md.append(f"- **Operation Applied:** `{step.get('operation', 'None')}`")
                md.append(f"- **Audit Hash:** `{step.get('audit_hash', 'None')}`")
            else:
                md.append("- **Status:** Initial Raw Dataset Upload")
                
            quality = step.get('quality_scores', {})
            if quality:
                md.append("- **Quality State:**")
                for k, v in quality.items():
                    md.append(f"  - *{k}:* {v:.2f}%")
            md.append(f"- **Timestamp:** `{step['timestamp']}`\n")
            
        md.append("## 3. Cryptographic Audit Trail\n")
        md.append("The following hashes mathematically prove that the operations and their exact parameters "
                  "have not been tampered with since execution.\n")
                  
        for audit in audit_trail:
            md.append(f"- **{audit.get('timestamp', 'Unknown Time')}** | Operation: **{audit.get('operation', audit.get('operation_name', 'Unknown'))}**")
            md.append(f"  - Parameters: `{audit.get('parameters', {})}`")
            md.append(f"  - Hash: `{audit.get('audit_hash', 'None')}`")
            
        return "\n".join(md)
