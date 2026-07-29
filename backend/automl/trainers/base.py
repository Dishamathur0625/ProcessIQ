import abc
from typing import Dict, Any, Tuple
import pandas as pd
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV

class BaseTrainer(abc.ABC):
    """
    Abstract base class for all Model Trainers.
    Enforces deterministic hyperparameter search via scikit-learn.
    """
    
    def __init__(self, task: str, random_seed: int = 42):
        self.task = task
        self.random_seed = random_seed
        self.best_estimator = None
        self.best_params = {}
        
    @abc.abstractmethod
    def get_base_estimator(self):
        """Returns the uninstantiated base estimator (e.g. XGBClassifier)."""
        pass
        
    @abc.abstractmethod
    def get_hyperparameter_grid(self) -> Dict[str, list]:
        """Returns the hyperparameter search space."""
        pass
        
    def train(self, X_train: pd.DataFrame, y_train: pd.Series, strategy: str = "Random Search", n_trials: int = 10, cv: int = 5, scoring: str = "accuracy") -> Tuple[Any, Dict[str, Any]]:
        """
        Executes hyperparameter search using scikit-learn.
        Returns the fitted best_estimator and the best hyperparameters.
        """
        estimator = self.get_base_estimator()
        grid = self.get_hyperparameter_grid()
        
        if strategy == "Grid Search":
            search = GridSearchCV(
                estimator=estimator,
                param_grid=grid,
                scoring=scoring,
                cv=cv,
                n_jobs=1 # Parallelism is handled by Orchestrator over candidates, not inside search to avoid oversubscription
            )
        else:
            # Default to Random Search
            search = RandomizedSearchCV(
                estimator=estimator,
                param_distributions=grid,
                n_iter=n_trials,
                scoring=scoring,
                cv=cv,
                random_state=self.random_seed,
                n_jobs=1
            )
            
        search.fit(X_train, y_train)
        
        self.best_estimator = search.best_estimator_
        self.best_params = search.best_params_
        
        return self.best_estimator, self.best_params
