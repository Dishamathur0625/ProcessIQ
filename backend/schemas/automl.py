from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ExecutionManifest(BaseModel):
    training_plan_id: str
    job_id: str
    dataset_fingerprint: str
    target_column: str
    task: str
    
    planner_version: str = "1.0"
    execution_version: str = "1.0"
    
    candidate_models: List[str]
    evaluation_metric: str
    cross_validation_strategy: str
    
    # AutoML Specific Settings
    parallel_jobs: int = Field(default=2, description="Number of models to train concurrently")
    random_seed: int = Field(default=42, description="Global random seed for reproducibility")
    hyperparameter_strategy: str = Field(default="Random Search", description="Grid Search, Random Search, etc.")
    n_trials: int = Field(default=10, description="Number of trials for Random Search")

class AutoMLStartRequest(BaseModel):
    job_id: str
    target_column: Optional[str] = None
    training_plan_id: Optional[str] = None # If None, generate from latest plan
    parallel_jobs: int = 2
    random_seed: int = 42
    hyperparameter_strategy: str = "Random Search"
    
class ModelMetrics(BaseModel):
    model_id: str
    model_name: str
    metrics: Dict[str, float]
    cv_scores: Optional[List[float]] = None
    hyperparameters: Dict[str, Any]
    training_time_sec: float
    
class AutoMLReport(BaseModel):
    session_id: str
    job_id: str
    best_model_id: str
    leaderboard: List[ModelMetrics]
    execution_time_sec: float
