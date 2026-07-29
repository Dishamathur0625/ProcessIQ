import uuid
from fastapi import UploadFile, HTTPException
from backend.storage.file_manager import FileManager

class DatasetService:
    ALLOWED_EXTENSIONS = {".csv"}
    ALLOWED_MIME_TYPES = {"text/csv", "application/vnd.ms-excel"}
    
    @classmethod
    def validate_upload(cls, file: UploadFile):
        if not file.filename.endswith(tuple(cls.ALLOWED_EXTENSIONS)):
            raise HTTPException(status_code=400, detail="Invalid file extension. Only CSV is allowed.")
        if file.content_type not in cls.ALLOWED_MIME_TYPES:
            raise HTTPException(status_code=400, detail="Invalid MIME type. Only CSV is allowed.")
            
    @classmethod
    def save_dataset(cls, file: UploadFile) -> str:
        cls.validate_upload(file)
        
        # In a real app we'd read chunks to enforce size limit before fully loading in memory.
        # But we'll do simple read here for v1.
        
        # Create a mock job_id as the dataset id for self-contained isolation
        job_id = str(uuid.uuid4())
        
        from backend.services.storage.factory import StorageFactory
        from backend.core.config import settings
        storage = StorageFactory.get_backend()
        
        bucket = settings.SUPABASE_BUCKET_DATASETS
        path = f"{job_id}/dataset.csv"
        
        storage.upload(bucket, path, file.file)
        
        return job_id
