import json
from typing import List, Dict, Any
from backend.storage.file_manager import file_manager

class ContextBuilder:
    @staticmethod
    def build_context(job_id: str, context_keys: List[str] = None) -> str:
        """
        Builds a comprehensive markdown/JSON context string based on the deterministic artifacts of a job.
        If context_keys is provided, only those specific artifacts are included to save tokens.
        """
        if not context_keys:
            # Default to pulling everything available for maximum context
            context_keys = ["dataset_profile", "quality_report", "feature_metadata", "pipeline_manifest"]
            
        context_parts = []
        
        context_parts.append(f"## Job Context: {job_id}")
        
        try:
            # Load metadata to find the available JSON artifacts
            metadata_str = file_manager.load_artifact(job_id, "METADATA")
            metadata = json.loads(metadata_str) if metadata_str else {}
        except Exception:
            metadata = {}

        if "dataset_profile" in context_keys:
            try:
                profile_str = file_manager.load_artifact(job_id, "PROFILE")
                if profile_str:
                    context_parts.append("### Dataset Profile\n```json\n" + profile_str + "\n```")
            except Exception:
                pass
                
        if "quality_report" in context_keys:
            try:
                quality_str = file_manager.load_artifact(job_id, "QUALITY_REPORT")
                if quality_str:
                    context_parts.append("### Quality Report\n```json\n" + quality_str + "\n```")
            except Exception:
                pass
                
        if "feature_metadata" in context_keys:
            try:
                feature_str = file_manager.load_artifact(job_id, "FEATURE_METADATA")
                if feature_str:
                    context_parts.append("### Feature Metadata & Lineage\n```json\n" + feature_str + "\n```")
            except Exception:
                pass
                
        if "pipeline_manifest" in context_keys:
            try:
                manifest_str = file_manager.load_artifact(job_id, "MANIFEST")
                if manifest_str:
                    context_parts.append("### Pipeline Manifest\n```json\n" + manifest_str + "\n```")
            except Exception:
                pass

        if "reports" in context_keys:
            try:
                report_str = file_manager.load_artifact(job_id, "REPORT")
                if report_str:
                    context_parts.append("### Final Report\n" + report_str)
            except Exception:
                pass

        if "visualizations" in context_keys:
            try:
                viz_str = file_manager.load_artifact(job_id, "VISUALIZATION")
                if viz_str:
                    # We might want to truncate or summarize this if it's too large, but we'll include it for now.
                    context_parts.append("### Visualizations\n```json\n" + viz_str + "\n```")
            except Exception:
                pass

        return "\n\n".join(context_parts)
