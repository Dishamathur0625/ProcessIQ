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

from fastapi.responses import StreamingResponse
import io

@router.get("/download/{job_id}")
def download_results(job_id: str, db: Session = Depends(get_db)):
    from backend.services.storage.factory import StorageFactory
    from backend.core.config import settings
    
    storage = StorageFactory.get_backend()
    bucket = settings.SUPABASE_BUCKET_PROCESSED
    path = f"{job_id}/processed_dataset.csv"
    
    try:
        content_bytes = storage.download(bucket, path)
        return StreamingResponse(
            io.BytesIO(content_bytes),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=processed_dataset_{job_id}.csv"}
        )
    except Exception as e:
        try:
            raw_bucket = settings.SUPABASE_BUCKET_DATASETS
            raw_path = f"{job_id}/dataset.csv"
            content_bytes = storage.download(raw_bucket, raw_path)
            return StreamingResponse(
                io.BytesIO(content_bytes),
                media_type="text/csv",
                headers={"Content-Disposition": f"attachment; filename=raw_dataset_{job_id}.csv"}
            )
        except Exception as e2:
            from fastapi import HTTPException
            raise HTTPException(status_code=404, detail=f"Dataset files not found for job: {str(e)}")
