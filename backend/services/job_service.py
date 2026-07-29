from sqlalchemy.orm import Session
from backend.db.models.job import PipelineJob
from backend.workers.tasks import execute_pipeline_task
from fastapi import HTTPException

class JobService:
    
    @classmethod
    def create_job(cls, db: Session, dataset_id: str, configuration: dict) -> str:
        job = PipelineJob(
            id=dataset_id, # Link directly for 1:1 in v1
            dataset_id=dataset_id,
            status="QUEUED",
            configuration=configuration
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        
        # Dispatch to Celery
        execute_pipeline_task.delay(job.id, configuration)
        
        return job.id

    @classmethod
    def get_job_status(cls, db: Session, job_id: str) -> dict:
        job = db.query(PipelineJob).filter(PipelineJob.id == job_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job not found")
            
        return {
            "job_id": job.id,
            "status": job.status,
            "created_at": job.created_at,
            "completed_at": job.completed_at,
            "error_message": job.error_message
        }
