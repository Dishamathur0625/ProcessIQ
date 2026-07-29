from backend.automl.trainers.base import BaseTrainer
from typing import Dict, Any

class CatBoostTrainer(BaseTrainer):
    """
    CatBoost trainer.
    """
    def __init__(self, model_id: str, task: str, random_seed: int = 42):
        super().__init__(task, random_seed)
        self.model_id = model_id
        
    def get_base_estimator(self):
        try:
            import catboost as cb
        except ImportError:
            raise ImportError("catboost is not installed. Please install it.")
            
        if self.task == "Regression":
            return cb.CatBoostRegressor(random_seed=self.random_seed, verbose=0)
        else:
            return cb.CatBoostClassifier(random_seed=self.random_seed, verbose=0)

    def get_hyperparameter_grid(self) -> Dict[str, list]:
        return {
            "iterations": [50, 100, 200],
            "depth": [4, 6, 8],
            "learning_rate": [0.01, 0.05, 0.1]
        }
