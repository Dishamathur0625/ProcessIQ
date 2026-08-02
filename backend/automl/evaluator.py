from typing import Dict, Any, List
import pandas as pd
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score, roc_auc_score,
    mean_squared_error, mean_absolute_error, r2_score
)
import numpy as np

class Evaluator:
    """
    Deterministically computes evaluation metrics using scikit-learn.
    """
    
    @staticmethod
    def evaluate(task: str, y_true: pd.Series, y_pred: np.ndarray, y_prob: np.ndarray = None) -> Dict[str, float]:
        metrics = {}
        if task == "Regression":
            mse = mean_squared_error(y_true, y_pred)
            metrics["rmse"] = float(np.sqrt(mse))
            metrics["mae"] = float(mean_absolute_error(y_true, y_pred))
            metrics["r2"] = float(r2_score(y_true, y_pred))
        else:
            is_binary = len(np.unique(y_true)) <= 2
            avg = "binary" if is_binary else "macro"
            
            metrics["accuracy"] = float(accuracy_score(y_true, y_pred))
            metrics["precision"] = float(precision_score(y_true, y_pred, average=avg, zero_division=0))
            metrics["recall"] = float(recall_score(y_true, y_pred, average=avg, zero_division=0))
            metrics["f1"] = float(f1_score(y_true, y_pred, average=avg, zero_division=0))
            
            if y_prob is not None and is_binary:
                # Use the probability of the positive class
                if y_prob.ndim == 2 and y_prob.shape[1] > 1:
                    prob_pos = y_prob[:, 1]
                else:
                    prob_pos = y_prob
                
                # Check if y_true has at least 2 classes
                if len(np.unique(y_true)) > 1:
                    metrics["roc_auc"] = float(roc_auc_score(y_true, prob_pos))
                else:
                    metrics["roc_auc"] = 0.5
                
        return metrics
