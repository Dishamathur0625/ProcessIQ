from backend.automl.trainers.base import BaseTrainer
from backend.automl.trainers.sklearn_trainer import SklearnTrainer
from backend.automl.trainers.xgboost_trainer import XGBoostTrainer
from backend.automl.trainers.lightgbm_trainer import LightGBMTrainer
from backend.automl.trainers.catboost_trainer import CatBoostTrainer

class TrainerFactory:
    """
    Factory to retrieve the appropriate trainer given a model_id.
    """
    
    @staticmethod
    def get_trainer(model_id: str, task: str, random_seed: int = 42) -> BaseTrainer:
        model_id_lower = model_id.lower()
        if "xgb" in model_id_lower:
            return XGBoostTrainer(model_id, task, random_seed)
        elif "lgb" in model_id_lower:
            return LightGBMTrainer(model_id, task, random_seed)
        elif "cat" in model_id_lower:
            return CatBoostTrainer(model_id, task, random_seed)
        elif "lr" in model_id_lower or "rf" in model_id_lower:
            return SklearnTrainer(model_id, task, random_seed)
        else:
            raise ValueError(f"Unknown model_id: {model_id}")
