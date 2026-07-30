import concurrent.futures
from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np
import time

from backend.schemas.automl import ExecutionManifest
from backend.automl.trainers.factory import TrainerFactory

class TrainingScheduler:
    """
    Manages parallel execution of candidate models using a Worker Pool.
    """
    
    @staticmethod
    def _train_candidate(model_id: str, manifest: ExecutionManifest, X_train: pd.DataFrame, y_train: pd.Series) -> Dict[str, Any]:
        """Worker function to train a single candidate."""
        start_time = time.time()
        try:
            trainer = TrainerFactory.get_trainer(model_id, manifest.task, manifest.random_seed)
            
            # Force smaller CV and trials for instant execution speed in the demo environment
            cv_folds = 2
            n_trials_val = min(2, manifest.n_trials)
            
            estimator, best_params = trainer.train(
                X_train, 
                y_train, 
                strategy=manifest.hyperparameter_strategy,
                n_trials=n_trials_val,
                cv=cv_folds,
                scoring="accuracy" if "Classification" in manifest.task else "neg_mean_squared_error" # Map internal string to sklearn scoring
            )
            
            duration = time.time() - start_time
            return {
                "model_id": model_id,
                "status": "SUCCESS",
                "estimator": estimator,
                "hyperparameters": best_params,
                "duration_sec": duration
            }
        except Exception as e:
            return {
                "model_id": model_id,
                "status": "FAILED",
                "error": str(e),
                "duration_sec": time.time() - start_time
            }

    @staticmethod
    def run_all(manifest: ExecutionManifest, X_train: pd.DataFrame, y_train: pd.Series) -> List[Dict[str, Any]]:
        """
        Dispatches all candidate models to a thread pool and returns the results.
        """
        results = []
        max_workers = manifest.parallel_jobs
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_model = {
                executor.submit(TrainingScheduler._train_candidate, m_id, manifest, X_train, y_train): m_id 
                for m_id in manifest.candidate_models
            }
            
            for future in concurrent.futures.as_completed(future_to_model):
                model_id = future_to_model[future]
                try:
                    res = future.result()
                    results.append(res)
                except Exception as exc:
                    results.append({
                        "model_id": model_id,
                        "status": "FAILED",
                        "error": str(exc),
                        "duration_sec": 0
                    })
                    
        return results
