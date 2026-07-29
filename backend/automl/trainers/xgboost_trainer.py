from backend.automl.trainers.base import BaseTrainer
from typing import Dict, Any

class XGBoostTrainer(BaseTrainer):
    """
    XGBoost trainer for both classification and regression.
    """
    def __init__(self, model_id: str, task: str, random_seed: int = 42):
        super().__init__(task, random_seed)
        self.model_id = model_id
        
    def get_base_estimator(self):
        try:
            import xgboost as xgb
        except ImportError:
            raise ImportError("xgboost is not installed. Please install it to use XGBoostTrainer.")
            
        if self.task == "Regression":
            return xgb.XGBRegressor(random_state=self.random_seed)
        else:
            # works for both binary and multi-class if configured correctly, but XGBClassifier handles it usually
            return xgb.XGBClassifier(random_state=self.random_seed, use_label_encoder=False, eval_metric="logloss")

    def get_hyperparameter_grid(self) -> Dict[str, list]:
        return {
            "n_estimators": [50, 100, 200],
            "max_depth": [3, 5, 7],
            "learning_rate": [0.01, 0.05, 0.1],
            "subsample": [0.8, 1.0],
            "colsample_bytree": [0.8, 1.0]
        }
