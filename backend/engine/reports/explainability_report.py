from typing import List, Any
from backend.engine.core.metadata import FeatureMetadata

class ExplainabilityReportGenerator:
    """
    Generates a human-readable markdown report explaining the Feature Engineering
    and Feature Selection lifecycle.
    """
    
    @staticmethod
    def generate(metadata_list: List[FeatureMetadata]) -> str:
        md = ["# ProcessIQ Feature Explainability Report\n"]
        md.append("This document tracks the cryptographic lineage of all engineered features, "
                  "explaining exactly how they were mathematically derived and why the Consensus Engine "
                  "approved or rejected them for Machine Learning.\n")
                  
        md.append("## 1. Feature Synthesis Overview\n")
        total_features = len(metadata_list)
        selected_features = len([m for m in metadata_list if m.is_selected])
        rejected_features = total_features - selected_features
        
        md.append(f"- **Total Candidate Features Generated:** {total_features}")
        md.append(f"- **Features Approved by Consensus:** {selected_features}")
        md.append(f"- **Features Rejected by Consensus:** {rejected_features}\n")
        
        md.append("## 2. Feature Lineage & Selection Rationale\n")
        
        # Sort by final rank if available, otherwise by name
        sorted_meta = sorted(metadata_list, key=lambda x: getattr(x, 'final_rank', 9999))
        
        for meta in sorted_meta:
            status = "✅ ACCEPTED" if meta.is_selected else "❌ REJECTED"
            md.append(f"### {meta.feature_name} ({status})")
            md.append(f"- **Source Column(s):** {', '.join(meta.source_columns)}")
            md.append(f"- **Mathematical Transformation:** `{meta.transformation_formula}`")
            md.append(f"- **Engineering Method:** {meta.engineering_method}")
            
            md.append(f"- **Selection Reason:** {meta.selection_reason}")
            
            if meta.selection_history:
                md.append("- **Algorithm Voting History:**")
                for algo, score in meta.selection_history.items():
                    md.append(f"  - *{algo}:* {score:.3f}")
            else:
                md.append("- **Algorithm Voting History:** None (Bypassed or Error)")
                
            md.append("\n")
            
        return "\n".join(md)
