import os
from typing import BinaryIO
from backend.services.storage.base import StorageBackend
from backend.core.config import settings

class SupabaseStorageBackend(StorageBackend):
    """
    Implements Supabase Storage.
    """
    
    def __init__(self):
        try:
            from supabase import create_client, Client
            
            if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
                raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env")
                
            self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_ROLE_KEY)
        except ImportError:
            raise ImportError("supabase package is required for SupabaseStorageBackend. Install with `pip install supabase`.")
            
    def upload(self, bucket: str, path: str, file_obj: BinaryIO) -> str:
        # Read the file content
        content = file_obj.read()
        
        # Upload to Supabase
        res = self.client.storage.from_(bucket).upload(path, content, {"upsert": "true"})
        if not hasattr(res, 'json') and type(res) == dict and 'error' in res:
             raise Exception(f"Supabase upload error: {res['error']}")
             
        return self.get_url(bucket, path)

    def download(self, bucket: str, path: str) -> bytes:
        res = self.client.storage.from_(bucket).download(path)
        return res

    def delete(self, bucket: str, path: str) -> bool:
        res = self.client.storage.from_(bucket).remove([path])
        return len(res) > 0

    def exists(self, bucket: str, path: str) -> bool:
        # Check by attempting to list the specific path
        directory = os.path.dirname(path)
        filename = os.path.basename(path)
        
        try:
            files = self.client.storage.from_(bucket).list(directory)
            for f in files:
                if f.get("name") == filename:
                    return True
        except Exception:
            pass
        return False

    def get_url(self, bucket: str, path: str) -> str:
        res = self.client.storage.from_(bucket).get_public_url(path)
        return res
