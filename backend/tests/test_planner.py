import pytest
from backend.planner.target_detector import TargetDetector
from backend.planner.task_detector import TaskDetector
from backend.planner.readiness import ReadinessAnalyzer
from backend.planner.model_recommender import ModelRecommender
from backend.planner.evaluation import EvaluationPlanner
from backend.planner.training_plan import TrainingPlanGenerator

def test_target_detector():
    metadata = {
        "row_count": 1000,
        "features": {
            "id": {"inferred_type": "integer", "is_identifier": True},
            "age": {"inferred_type": "integer"},
            "target": {"inferred_type": "integer", "unique_count": 2, "missing_ratio": 0.0}
        }
    }
    result = TargetDetector.detect_targets(metadata)
    assert len(result["candidates"]) == 1
    assert result["candidates"][0]["column"] == "target"
    assert result["candidates"][0]["predicted_task"] == "Binary Classification"

def test_task_detector():
    metadata = {
        "features": {
            "price": {"inferred_type": "float", "unique_count": 500}
        }
    }
    task = TaskDetector.detect_task(metadata, "price")
    assert task == "Regression"

def test_readiness_analyzer():
    metadata = {
        "row_count": 50, # Tiny dataset
        "features": {
            "label": {"inferred_type": "integer", "unique_count": 2, "missing_ratio": 0.0},
            "f1": {"inferred_type": "float", "missing_ratio": 0.6}
        }
    }
    quality = {"warnings": []}
    task = "Binary Classification"
    
    result = ReadinessAnalyzer.analyze_readiness(metadata, quality, "label", task)
    assert result["readiness_score"] < 100
    assert any("Tiny dataset" in issue for issue in result["issues"])
    assert any("missing values" in issue for issue in result["issues"])

def test_model_recommender():
    metadata = {
        "row_count": 200000,
        "features": {
            "f1": {"inferred_type": "categorical"},
            "f2": {"inferred_type": "categorical"},
            "f3": {"inferred_type": "categorical"},
            "f4": {"inferred_type": "categorical"},
            "f5": {"inferred_type": "categorical"},
            "f6": {"inferred_type": "categorical"}
        }
    }
    task = "Binary Classification"
    
    recs = ModelRecommender.recommend(task, metadata)
    assert len(recs) > 0
    # Should recommend CatBoost highly because of many categoricals
    catboost = next(r for r in recs if "CatBoost" in r["model_name"])
    assert "Many categoricals" in str(catboost["score_breakdown"])

def test_evaluation_planner():
    readiness = {"issues": ["Class imbalance detected in target column"]}
    strategy = EvaluationPlanner.plan("Binary Classification", readiness)
    
    assert "PR-AUC" in strategy["metrics"]
    assert "Stratified 5-Fold CV" in strategy["cross_validation"]

def test_training_plan_generator():
    readiness = {"readiness_score": 90, "is_ready": True, "issues": []}
    models = [{"model_name": "XGBoost", "suitability_score": 85}]
    evaluation = {"cross_validation": "5-Fold CV", "metrics": ["RMSE"]}
    
    plan = TrainingPlanGenerator.generate(
        dataset_fingerprint="test_fp",
        target_column="price",
        task="Regression",
        readiness=readiness,
        models=models,
        evaluation=evaluation
    )
    
    assert plan["metadata"]["planner_version"] == "1.0"
    assert plan["configuration"]["task"] == "Regression"
    assert plan["configuration"]["target_column"] == "price"
