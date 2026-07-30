from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from backend.core.database import get_db
from backend.schemas.automl import AutoMLStartRequest, AutoMLReport
from backend.automl.manifest import ManifestGenerator
from backend.automl.orchestrator import AutoMLOrchestrator
from backend.automl.reporter import AutoMLReporter
from backend.services.artifact_service import ArtifactService

router = APIRouter(tags=["AutoML"])

# In-memory store for sessions during this demo since DB might be down
_SESSIONS: Dict[str, AutoMLReport] = {}

def run_automl_background(manifest_dict: dict):
    # Reconstruct manifest
    from backend.schemas.automl import ExecutionManifest
    manifest = ExecutionManifest(**manifest_dict)
    
    # Execute orchestrator
    try:
        report = AutoMLOrchestrator.execute(manifest)
        _SESSIONS[manifest.job_id] = report
        
        # Save report as artifact
        md_content = AutoMLReporter.generate_markdown(report)
        # Normally save via ArtifactService if db was active
        print(f"AutoML Completed for {manifest.job_id}")
    except Exception as e:
        print(f"AutoML Failed for {manifest.job_id}: {e}")
        _SESSIONS[manifest.job_id] = {"error": str(e), "status": "FAILED"}

@router.post("/start")
def start_automl(req: AutoMLStartRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # 1. Get training plan
    try:
        target_col = req.target_column or "target"
        task = "Binary Classification"
        models = [{"model_id": "lr_clf"}, {"model_id": "rf_clf"}]
        
        # Dynamically inspect dataset to determine task and models
        try:
            df = ArtifactService.load_dataframe(db, req.job_id, "processed_dataset.csv")
            if target_col not in df.columns and len(df.columns) > 0:
                target_col = df.columns[-1]
                
            unique_vals = df[target_col].dropna().unique()
            import pandas as pd
            is_numeric = pd.api.types.is_numeric_dtype(df[target_col])
            
            if is_numeric and len(unique_vals) > 10:
                task = "Regression"
                models = [{"model_id": "lr"}, {"model_id": "rf_reg"}]
            elif len(unique_vals) <= 20:
                task = "Binary Classification" if len(unique_vals) == 2 else "Multi-class Classification"
                models = [{"model_id": "lr_clf"}, {"model_id": "rf_clf"}]
        except Exception as e:
            print(f"AutoML task detection fallback inspection failed: {e}")
            
        training_plan = {
            "metadata": {"plan_id": "plan-123", "dataset_fingerprint": "fp-123", "planner_version": "1.0"},
            "configuration": {
                "target_column": target_col,
                "task": task,
                "recommended_models": models,
                "evaluation_strategy": {"metrics": ["accuracy" if "Classification" in task else "rmse"], "cross_validation": "5-Fold CV"}
            }
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Failed to initialize training plan: {str(e)}")
        
    settings = {
        "parallel_jobs": req.parallel_jobs,
        "random_seed": req.random_seed,
        "hyperparameter_strategy": req.hyperparameter_strategy
    }
    
    # Generate Manifest
    manifest = ManifestGenerator.generate(req.job_id, training_plan, settings)
    
    # Launch Background Task
    _SESSIONS[req.job_id] = {"status": "RUNNING"}
    background_tasks.add_task(run_automl_background, manifest.dict())
    
    return {"message": "AutoML session started", "job_id": req.job_id}

@router.get("/{job_id}")
def get_automl_status(job_id: str):
    session = _SESSIONS.get(job_id)
    if not session:
        return {"status": "NOT_STARTED"}
    
    if isinstance(session, dict) and session.get("status") in ["RUNNING", "FAILED"]:
        return session
        
    return {
        "status": "COMPLETED",
        "best_model": session.best_model_id,
        "leaderboard": [m.dict() for m in session.leaderboard]
    }

@router.get("/{job_id}/leaderboard")
def get_automl_leaderboard(job_id: str):
    session = _SESSIONS.get(job_id)
    if not session or isinstance(session, dict):
        raise HTTPException(status_code=404, detail="Leaderboard not ready")
        
    return {"leaderboard": [m.dict() for m in session.leaderboard]}

@router.get("/{job_id}/report")
def get_automl_report(job_id: str):
    session = _SESSIONS.get(job_id)
    if not session or isinstance(session, dict):
        raise HTTPException(status_code=404, detail="Report not ready")
        
    md = AutoMLReporter.generate_markdown(session)
    return {"report_markdown": md}

@router.post("/{job_id}/cancel")
def cancel_automl(job_id: str):
    # In a real system, we'd flag the session in DB and threads would check it
    return {"message": "Cancellation requested (not fully implemented)"}
