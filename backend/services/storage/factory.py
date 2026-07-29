from backend.services.storage.base import StorageBackend
from backend.services.storage.local import LocalStorageBackend
from backend.core.config import settings

class StorageFactory:
    """
    Factory to retrieve the appropriate StorageBackend based on configuration.
    """
    
    _instance = None
    
    @classmethod
    def get_backend(cls) -> StorageBackend:
        if cls._instance is not None:
            return cls._instance
            
        provider = settings.STORAGE_PROVIDER.lower()
        if provider == "supabase":
            from backend.services.storage.supabase_storage import SupabaseStorageBackend
            cls._instance = SupabaseStorageBackend()
        else:
            cls._instance = LocalStorageBackend()
            
        return cls._instance
