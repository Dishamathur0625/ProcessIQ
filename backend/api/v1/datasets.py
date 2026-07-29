from fastapi import APIRouter, UploadFile, File
from backend.services.dataset_service import DatasetService

router = APIRouter(tags=["Datasets"])

@router.post("/upload")
def upload_dataset(file: UploadFile = File(...)):
    """
    Uploads a dataset to the system and returns a unique ID to be used for pipelines.
    """
    job_id = DatasetService.save_dataset(file)
    return {"dataset_id": job_id, "message": "Dataset uploaded successfully"}
