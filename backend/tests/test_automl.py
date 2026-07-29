import pytest
import pandas as pd
import numpy as np

from backend.schemas.automl import ExecutionManifest
from backend.automl.evaluator import Evaluator
from backend.automl.explainer import Explainer
from backend.automl.trainers.sklearn_trainer import SklearnTrainer

def test_evaluator_regression():
    y_true = pd.Series([1.0, 2.0, 3.0])
    y_pred = np.array([1.1, 1.9, 3.0])
    metrics = Evaluator.evaluate("Regression", y_true, y_pred)
    assert "rmse" in metrics
    assert "mae" in metrics
    assert "r2" in metrics
    assert metrics["rmse"] < 0.2

def test_evaluator_classification():
    y_true = pd.Series([0, 1, 0, 1])
    y_pred = np.array([0, 1, 0, 0])
    y_prob = np.array([0.1, 0.9, 0.2, 0.4])
    metrics = Evaluator.evaluate("Binary Classification", y_true, y_pred, y_prob)
    assert "accuracy" in metrics
    assert "roc_auc" in metrics
    assert metrics["accuracy"] == 0.75

def test_sklearn_trainer():
    # Simple XOR dataset
    X_train = pd.DataFrame({"f1": [0, 0, 1, 1], "f2": [0, 1, 0, 1]})
    y_train = pd.Series([0, 1, 1, 0])
    
    trainer = SklearnTrainer(model_id="rf_clf", task="Binary Classification")
    estimator, params = trainer.train(X_train, y_train, strategy="Grid Search", cv=2)
    
    assert estimator is not None
    assert "n_estimators" in params

def test_explainer():
    X_val = pd.DataFrame({"f1": [1, 2, 3], "f2": [4, 5, 6]})
    y_val = pd.Series([0, 1, 0])
    
    # Mock estimator with feature_importances_
    class MockEstimator:
        feature_importances_ = np.array([0.2, 0.8])
        
    res = Explainer.get_feature_importance(MockEstimator(), X_val, y_val, "Binary Classification")
    assert res["method"] == "Native"
    assert len(res["data"][0]["x"]) == 2
