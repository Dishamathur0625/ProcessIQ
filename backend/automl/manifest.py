from backend.schemas.automl import ExecutionManifest
from typing import Dict, Any, List

class ManifestGenerator:
    """
    Transitions a deterministic Training Plan into an Execution Manifest.
    """
    
    @staticmethod
    def generate(job_id: str, training_plan: Dict[str, Any], settings: Dict[str, Any] = None) -> ExecutionManifest:
        if settings is None:
            settings = {}
            
        config = training_plan.get("configuration", {})
        meta = training_plan.get("metadata", {})
        
        candidates = [m.get("model_id") for m in config.get("recommended_models", []) if "model_id" in m]
        if not candidates:
            # Fallback if names are passed but not ids
            candidates = [m.get("model_name").lower().replace(" ", "_") for m in config.get("recommended_models", [])]
            
        return ExecutionManifest(
            training_plan_id=meta.get("plan_id", "unknown"),
            job_id=job_id,
            dataset_fingerprint=meta.get("dataset_fingerprint", "unknown"),
            target_column=config.get("target_column", ""),
            task=config.get("task", ""),
            planner_version=meta.get("planner_version", "1.0"),
            execution_version="1.0",
            candidate_models=candidates,
            evaluation_metric=config.get("evaluation_strategy", {}).get("metrics", ["Accuracy"])[0],
            cross_validation_strategy=config.get("evaluation_strategy", {}).get("cross_validation", "5-Fold CV"),
            parallel_jobs=settings.get("parallel_jobs", 2),
            random_seed=settings.get("random_seed", 42),
            hyperparameter_strategy=settings.get("hyperparameter_strategy", "Random Search"),
            n_trials=settings.get("n_trials", 10)
        )
