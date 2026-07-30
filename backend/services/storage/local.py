import os
import shutil
from typing import BinaryIO
from backend.services.storage.base import StorageBackend

class LocalStorageBackend(StorageBackend):
    """
    Implements local file system storage.
    """
    
    def __init__(self, base_dir: str = None):
        if base_dir is None:
            # Resolve relative to the project root directory (which is 4 levels up from this file)
            current_file = os.path.abspath(__file__)
            project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(current_file))))
            self.base_dir = os.path.join(project_root, "storage")
        else:
            self.base_dir = os.path.abspath(base_dir)
        os.makedirs(self.base_dir, exist_ok=True)
        
    def _get_full_path(self, bucket: str, path: str) -> str:
        # Sanitize path to prevent directory traversal
        bucket_dir = os.path.join(self.base_dir, bucket)
        os.makedirs(bucket_dir, exist_ok=True)
        return os.path.join(bucket_dir, path)

    def upload(self, bucket: str, path: str, file_obj: BinaryIO) -> str:
        full_path = self._get_full_path(bucket, path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        with open(full_path, "wb") as f:
            shutil.copyfileobj(file_obj, f)
            
        return full_path

    def download(self, bucket: str, path: str) -> bytes:
        full_path = self._get_full_path(bucket, path)
        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File {path} not found in bucket {bucket}")
            
        with open(full_path, "rb") as f:
            return f.read()

    def delete(self, bucket: str, path: str) -> bool:
        full_path = self._get_full_path(bucket, path)
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False

    def exists(self, bucket: str, path: str) -> bool:
        return os.path.exists(self._get_full_path(bucket, path))

    def get_url(self, bucket: str, path: str) -> str:
        return f"local://{bucket}/{path}"
