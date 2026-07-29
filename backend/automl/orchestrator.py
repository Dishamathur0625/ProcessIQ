import pandas as pd
import uuid
import datetime
from typing import Dict, Any
from sklearn.model_selection import train_test_split

from backend.schemas.automl import ExecutionManifest, ModelMetrics, AutoMLReport
from backend.automl.scheduler import TrainingScheduler
from backend.automl.evaluator import Evaluator
from backend.automl.explainer import Explainer
from backend.automl.storage import ModelStorage
from backend.services.artifact_service import ArtifactService
from backend.db.session import SessionLocal

class AutoMLOrchestrator:
    """
    Main pipeline loop for Model Training & AutoML.
    """
    
    @staticmethod
    def execute(manifest: ExecutionManifest) -> AutoMLReport:
        session_id = str(uuid.uuid4())
        
        # 1. Load Data
        db = SessionLocal()
        try:
            # Assumes dataset artifact exists. We'd normally use DatasetService, but ArtifactService works if we saved the df
            df = ArtifactService.load_dataframe(db, manifest.job_id, "processed_dataset.csv")
        except Exception as e:
            # Fallback if we don't have the artifact helper
            import os
            from backend.core.config import settings
            path = os.path.join(settings.ARTIFACT_DIR, manifest.job_id, "processed_dataset.csv")
            df = pd.read_csv(path)
        finally:
            db.close()
            
        # 2. Split Data
        if manifest.target_column not in df.columns:
            raise ValueError(f"Target column {manifest.target_column} not found in dataset.")
            
        X = df.drop(columns=[manifest.target_column])
        y = df[manifest.target_column]
        
        # Determine stratify if classification
        stratify = y if "Classification" in manifest.task else None
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, 
            test_size=0.2, 
            random_state=manifest.random_seed,
            stratify=stratify
        )
        
        # 3. Schedule and Train
        results = TrainingScheduler.run_all(manifest, X_train, y_train)
        
        # 4. Evaluate & Explain
        leaderboard = []
        for res in results:
            if res["status"] == "SUCCESS":
                estimator = res["estimator"]
                
                # Predict
                y_pred = estimator.predict(X_test)
                y_prob = None
                if hasattr(estimator, "predict_proba"):
                    y_prob = estimator.predict_proba(X_test)
                    
                # Evaluate
                metrics = Evaluator.evaluate(manifest.task, y_test, y_pred, y_prob)
                
                # Explain
                explanation = Explainer.get_feature_importance(estimator, X_test, y_test, manifest.task, manifest.random_seed)
                
                # Save Model
                model_path = ModelStorage.save_model(manifest.job_id, res["model_id"], estimator)
                
                # Normally save to DB here...
                
                leaderboard.append(ModelMetrics(
                    model_id=res["model_id"],
                    model_name=res["model_id"], # UI uses name
                    metrics=metrics,
                    hyperparameters=res["hyperparameters"],
                    training_time_sec=res["duration_sec"]
                ))
                
        # 5. Build Report
        # Sort leaderboard
        sort_metric = "rmse" if manifest.task == "Regression" else "roc_auc"
        sort_asc = True if manifest.task == "Regression" else False
        
        if sort_metric not in leaderboard[0].metrics and "accuracy" in leaderboard[0].metrics:
             sort_metric = "accuracy"
             sort_asc = False
             
        leaderboard.sort(key=lambda x: x.metrics.get(sort_metric, 0), reverse=not sort_asc)
        
        best_model_id = leaderboard[0].model_id if leaderboard else ""
        
        report = AutoMLReport(
            session_id=session_id,
            job_id=manifest.job_id,
            best_model_id=best_model_id,
            leaderboard=leaderboard,
            execution_time_sec=sum(m.training_time_sec for m in leaderboard)
        )
        
        return report
