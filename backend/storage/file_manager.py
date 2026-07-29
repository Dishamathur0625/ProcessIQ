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
