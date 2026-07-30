from backend.automl.trainers.base import BaseTrainer
from typing import Dict, Any

class SklearnTrainer(BaseTrainer):
    """
    Standard Scikit-learn trainer covering Logistic Regression and Random Forest.
    """
    def __init__(self, model_id: str, task: str, random_seed: int = 42):
        super().__init__(task, random_seed)
        self.model_id = model_id
        
    def get_base_estimator(self):
        if self.task == "Regression":
            if self.model_id == "lr":
                from sklearn.linear_model import LinearRegression
                return LinearRegression()
            elif self.model_id == "rf_reg":
                from sklearn.ensemble import RandomForestRegressor
                return RandomForestRegressor(random_state=self.random_seed)
        else:
            if self.model_id == "lr_clf":
                from sklearn.linear_model import LogisticRegression
                return LogisticRegression(random_state=self.random_seed, max_iter=1000)
            elif self.model_id in ["rf_clf", "rf_multi"]:
                from sklearn.ensemble import RandomForestClassifier
                return RandomForestClassifier(random_state=self.random_seed)
                
        raise ValueError(f"Unsupported sklearn model id: {self.model_id}")

    def get_hyperparameter_grid(self) -> Dict[str, list]:
        if "rf" in self.model_id:
            return {
                "n_estimators": [5, 10, 20],
                "max_depth": [None, 5, 10],
                "min_samples_split": [2, 5]
            }
        elif "lr_clf" in self.model_id:
            return {
                "C": [0.1, 1.0, 10.0],
                "solver": ["lbfgs", "liblinear"]
            }
        else:
            # Linear Regression
            return {
                "fit_intercept": [True, False]
            }
