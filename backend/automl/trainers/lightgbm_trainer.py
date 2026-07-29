from backend.automl.trainers.base import BaseTrainer
from typing import Dict, Any

class LightGBMTrainer(BaseTrainer):
    """
    LightGBM trainer.
    """
    def __init__(self, model_id: str, task: str, random_seed: int = 42):
        super().__init__(task, random_seed)
        self.model_id = model_id
        
    def get_base_estimator(self):
        try:
            import lightgbm as lgb
        except ImportError:
            raise ImportError("lightgbm is not installed. Please install it.")
            
        if self.task == "Regression":
            return lgb.LGBMRegressor(random_state=self.random_seed)
        else:
            return lgb.LGBMClassifier(random_state=self.random_seed)

    def get_hyperparameter_grid(self) -> Dict[str, list]:
        return {
            "n_estimators": [50, 100, 200],
            "max_depth": [-1, 5, 10],
            "learning_rate": [0.01, 0.05, 0.1],
            "num_leaves": [31, 63, 127]
        }
