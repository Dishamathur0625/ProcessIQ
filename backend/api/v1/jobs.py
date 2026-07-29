from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.services.job_service import JobService

router = APIRouter(tags=["Jobs"])

class PipelineConfigRequest(BaseModel):
    dataset_id: str
    pipeline: dict = {
        "validation": True,
        "cleaning": True,
        "feature_engineering": True,
        "feature_selection": True,
        "visualization": True,
        "reports": True
    }

@router.post("/pipeline/run")
def run_pipeline(request: PipelineConfigRequest, db: Session = Depends(get_db)):
    job_id = JobService.create_job(db, request.dataset_id, request.pipeline)
    return {"job_id": job_id, "message": "Pipeline execution queued successfully."}

@router.get("/job/{job_id}")
def get_job_status(job_id: str, db: Session = Depends(get_db)):
    return JobService.get_job_status(db, job_id)
