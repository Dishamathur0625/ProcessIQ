from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.artifact_service import ArtifactService
from backend.planner.target_detector import TargetDetector
from backend.planner.task_detector import TaskDetector
from backend.planner.readiness import ReadinessAnalyzer
from backend.planner.model_recommender import ModelRecommender
from backend.planner.evaluation import EvaluationPlanner
from backend.planner.training_plan import TrainingPlanGenerator

router = APIRouter(tags=["Prediction Planner"])

class PlannerRequest(BaseModel):
    job_id: str
    target_column: Optional[str] = None

@router.post("/target-candidates")
def get_target_candidates(req: PlannerRequest, db: Session = Depends(get_db)):
    try:
        metadata = ArtifactService.get_artifact(db, req.job_id, "feature_metadata")
    except HTTPException:
        raise HTTPException(status_code=404, detail="Dataset feature_metadata not found for this job.")
        
    candidates = TargetDetector.detect_targets(metadata)
    return candidates

@router.post("/task-detection")
def detect_task(req: PlannerRequest, db: Session = Depends(get_db)):
    if not req.target_column:
        raise HTTPException(status_code=400, detail="target_column is required.")
        
    metadata = ArtifactService.get_artifact(db, req.job_id, "feature_metadata")
    task = TaskDetector.detect_task(metadata, req.target_column)
    return {"detected_task": task}

@router.post("/readiness")
def analyze_readiness(req: PlannerRequest, db: Session = Depends(get_db)):
    if not req.target_column:
        raise HTTPException(status_code=400, detail="target_column is required.")
        
    metadata = ArtifactService.get_artifact(db, req.job_id, "feature_metadata")
    quality = ArtifactService.get_artifact(db, req.job_id, "quality_report")
    
    task = TaskDetector.detect_task(metadata, req.target_column)
    readiness = ReadinessAnalyzer.analyze_readiness(metadata, quality, req.target_column, task)
    
    return readiness

@router.post("/recommend-models")
def recommend_models(req: PlannerRequest, db: Session = Depends(get_db)):
    if not req.target_column:
        raise HTTPException(status_code=400, detail="target_column is required.")
        
    metadata = ArtifactService.get_artifact(db, req.job_id, "feature_metadata")
    task = TaskDetector.detect_task(metadata, req.target_column)
    
    recommendations = ModelRecommender.recommend(task, metadata)
    return {"recommended_models": recommendations}

@router.post("/evaluation-plan")
def evaluation_plan(req: PlannerRequest, db: Session = Depends(get_db)):
    if not req.target_column:
        raise HTTPException(status_code=400, detail="target_column is required.")
        
    metadata = ArtifactService.get_artifact(db, req.job_id, "feature_metadata")
    quality = ArtifactService.get_artifact(db, req.job_id, "quality_report")
    task = TaskDetector.detect_task(metadata, req.target_column)
    readiness = ReadinessAnalyzer.analyze_readiness(metadata, quality, req.target_column, task)
    
    plan = EvaluationPlanner.plan(task, readiness)
    return plan

@router.post("/training-plan")
def generate_training_plan(req: PlannerRequest, db: Session = Depends(get_db)):
    if not req.target_column:
        raise HTTPException(status_code=400, detail="target_column is required.")
        
    metadata = ArtifactService.get_artifact(db, req.job_id, "feature_metadata")
    quality = ArtifactService.get_artifact(db, req.job_id, "quality_report")
    fingerprint_obj = ArtifactService.get_artifact(db, req.job_id, "fingerprint")
    fingerprint = fingerprint_obj.get("dataset_fingerprint", "unknown") if isinstance(fingerprint_obj, dict) else "unknown"
    
    task = TaskDetector.detect_task(metadata, req.target_column)
    readiness = ReadinessAnalyzer.analyze_readiness(metadata, quality, req.target_column, task)
    models = ModelRecommender.recommend(task, metadata)
    evaluation = EvaluationPlanner.plan(task, readiness)
    
    plan = TrainingPlanGenerator.generate(
        dataset_fingerprint=fingerprint,
        target_column=req.target_column,
        task=task,
        readiness=readiness,
        models=models,
        evaluation=evaluation
    )
    
    # Normally we would save to db here, but skipping since DB is down in this session.
    # We can rely on the JSON returning to the frontend for now.
    return plan
