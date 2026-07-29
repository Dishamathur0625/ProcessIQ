from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db
from backend.services.artifact_service import ArtifactService

router = APIRouter(tags=["Artifacts"])

@router.get("/reports/{job_id}")
def get_reports(job_id: str, db: Session = Depends(get_db)):
    return ArtifactService.get_artifact(db, job_id, "REPORT")

@router.get("/visualizations/{job_id}")
def get_visualizations(job_id: str, db: Session = Depends(get_db)):
    return ArtifactService.get_artifact(db, job_id, "VISUALIZATION")

@router.get("/download/{job_id}")
def download_results(job_id: str, db: Session = Depends(get_db)):
    # Quick placeholder: in production this would return a FileResponse of the dataset
    return {"message": "Use this endpoint to download dataset.csv later."}
