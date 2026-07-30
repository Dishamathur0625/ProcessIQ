import os
import shutil
from pathlib import Path
from backend.core.config import settings

class FileManager:
    @staticmethod
    def _ensure_dir(path: str):
        os.makedirs(path, exist_ok=True)

    @staticmethod
    def get_job_dir(job_id: str) -> str:
        job_dir = os.path.join(settings.UPLOAD_DIR, "jobs", job_id)
        FileManager._ensure_dir(job_dir)
        return job_dir
        
    @staticmethod
    def save_upload(job_id: str, filename: str, content: bytes) -> str:
        job_dir = FileManager.get_job_dir(job_id)
        file_path = os.path.join(job_dir, filename)
        with open(file_path, "wb") as f:
            f.write(content)
        return file_path

    @staticmethod
    def save_artifact(job_id: str, category: str, filename: str, content: str) -> str:
        """
        category: "reports", "visualizations", "metadata"
        """
        job_dir = FileManager.get_job_dir(job_id)
        cat_dir = os.path.join(job_dir, category)
        FileManager._ensure_dir(cat_dir)
        
        file_path = os.path.join(cat_dir, filename)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        return file_path

    @staticmethod
    def read_artifact(file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Artifact not found at {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def load_artifact(job_id: str, category_key: str) -> str:
        """
        Loads artifact content from storage (local or Supabase).
        """
        from backend.core.config import settings
        from backend.services.storage.factory import StorageFactory
        
        category_mapping = {
            "METADATA": (settings.SUPABASE_BUCKET_ARTIFACTS, f"{job_id}/metadata.json", "metadata", "metadata.json"),
            "PROFILE": (settings.SUPABASE_BUCKET_ARTIFACTS, f"{job_id}/profile.json", "metadata", "profile.json"),
            "QUALITY_REPORT": (settings.SUPABASE_BUCKET_ARTIFACTS, f"{job_id}/quality_report.json", "reports", "quality_report.json"),
            "FEATURE_METADATA": (settings.SUPABASE_BUCKET_ARTIFACTS, f"{job_id}/feature_metadata.json", "metadata", "feature_metadata.json"),
            "MANIFEST": (settings.SUPABASE_BUCKET_MANIFESTS, f"{job_id}/manifest.json", "metadata", "manifest.json"),
            "REPORT": (settings.SUPABASE_BUCKET_REPORTS, f"{job_id}/pipeline_report.md", "reports", "pipeline_report.md"),
            "VISUALIZATION": (settings.SUPABASE_BUCKET_VISUALIZATIONS, f"{job_id}/viz_spec.json", "visualizations", "viz_spec.json")
        }
        
        mapping = category_mapping.get(category_key.upper())
        if not mapping:
            raise ValueError(f"Unknown artifact category: {category_key}")
            
        bucket, storage_path, local_cat, local_filename = mapping
        
        # Try local first if local provider is active
        if settings.STORAGE_PROVIDER.lower() == "local":
            job_dir = FileManager.get_job_dir(job_id)
            file_path = os.path.join(job_dir, local_cat, local_filename)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
                    
        # Otherwise, try from storage backend (Supabase or LocalStorageBackend)
        try:
            storage = StorageFactory.get_backend()
            content_bytes = storage.download(bucket, storage_path)
            return content_bytes.decode("utf-8")
        except Exception as e:
            # Fallback to local disk path
            job_dir = FileManager.get_job_dir(job_id)
            file_path = os.path.join(job_dir, local_cat, local_filename)
            if os.path.exists(file_path):
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            raise FileNotFoundError(f"Artifact {category_key} not found: {e}")

file_manager = FileManager
