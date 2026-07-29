import os
import tempfile
import joblib
from typing import Any
from backend.core.config import settings
from backend.services.storage.factory import StorageFactory

class ModelStorage:
    """
    Standardized serialization for models.
    Saves models via StorageFactory.
    """
    
    @staticmethod
    def save_model(job_id: str, model_id: str, estimator: Any) -> str:
        """
        Saves the estimator based on its type and returns the file path.
        """
        storage = StorageFactory.get_backend()
        bucket = settings.SUPABASE_BUCKET_MODELS
        
        # We need a temporary file since libraries expect local file paths to save
        fd, temp_path = tempfile.mkstemp()
        os.close(fd)
        
        try:
            # Determine format and save to temp_path
            if hasattr(estimator, "save_model") and "XGB" in type(estimator).__name__:
                filename = f"{model_id}.json"
                estimator.save_model(temp_path)
            elif hasattr(estimator, "booster_") and "LGBM" in type(estimator).__name__:
                filename = f"{model_id}.txt"
                estimator.booster_.save_model(temp_path)
            elif hasattr(estimator, "save_model") and "CatBoost" in type(estimator).__name__:
                filename = f"{model_id}.cbm"
                estimator.save_model(temp_path)
            else:
                # Fallback to joblib for scikit-learn or others
                filename = f"{model_id}.joblib"
                joblib.dump(estimator, temp_path)
                
            path = f"{job_id}/{filename}"
            with open(temp_path, "rb") as f:
                storage.upload(bucket, path, f)
                
            return path
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)
