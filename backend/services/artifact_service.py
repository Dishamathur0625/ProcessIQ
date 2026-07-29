from sqlalchemy.orm import Session
from backend.db.models.artifact import PipelineArtifact
from backend.services.storage.factory import StorageFactory
from fastapi import HTTPException
import json
import io
import pandas as pd

from backend.core.config import settings

class ArtifactService:
    @classmethod
    def get_artifact(cls, db: Session, job_id: str, artifact_type: str) -> dict:
        artifact = db.query(PipelineArtifact).filter(
            PipelineArtifact.job_id == job_id,
            PipelineArtifact.artifact_type == artifact_type
        ).first()
        
        if not artifact:
            raise HTTPException(status_code=404, detail=f"Artifact of type {artifact_type} not found for job {job_id}")
            
        if artifact.content_json:
            return artifact.content_json
            
        if artifact.file_path:
            storage = StorageFactory.get_backend()
            # Determine bucket from category/artifact_type or fallback to artifacts
            bucket = settings.SUPABASE_BUCKET_ARTIFACTS 
            try:
                content = storage.download(bucket, artifact.file_path).decode("utf-8")
                return json.loads(content)
            except:
                return {"content": "Failed to load from storage"}
                
        return {}

    @classmethod
    def load_dataframe(cls, db: Session, job_id: str, filename: str) -> pd.DataFrame:
        storage = StorageFactory.get_backend()
        bucket = settings.SUPABASE_BUCKET_ARTIFACTS
        path = f"{job_id}/{filename}"
        
        try:
            content_bytes = storage.download(bucket, path)
            df = pd.read_csv(io.BytesIO(content_bytes))
            return df
        except Exception as e:
            # Fallback to local disk path if not in storage bucket layout yet
            import os
            from backend.core.config import settings
            local_path = os.path.join(settings.ARTIFACT_DIR, job_id, filename)
            if os.path.exists(local_path):
                 return pd.read_csv(local_path)
            raise ValueError(f"Could not load dataframe {filename} for job {job_id}: {e}")

