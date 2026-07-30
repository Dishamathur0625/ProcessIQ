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
from backend.core.database import SessionLocal

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
            # Resilient fallback using StorageFactory directly to fetch the processed dataset
            try:
                from backend.services.storage.factory import StorageFactory
                from backend.core.config import settings
                import io
                storage = StorageFactory.get_backend()
                bucket = settings.SUPABASE_BUCKET_PROCESSED
                path = f"{manifest.job_id}/processed_dataset.csv"
                content_bytes = storage.download(bucket, path)
                df = pd.read_csv(io.BytesIO(content_bytes))
            except Exception as e2:
                import os
                from backend.core.config import settings
                # Try all possible local paths
                paths = [
                    os.path.join("storage", "processed", manifest.job_id, "processed_dataset.csv"),
                    os.path.join("storage", "artifacts", manifest.job_id, "processed_dataset.csv"),
                    os.path.join(settings.UPLOAD_DIR, "jobs", manifest.job_id, "processed", "processed_dataset.csv"),
                ]
                df = None
                for p in paths:
                    if os.path.exists(p):
                        df = pd.read_csv(p)
                        break
                if df is None:
                    raise ValueError(f"Could not load processed dataset: {e} / {e2}")
        finally:
            db.close()
            
        # 2. Split Data
        target_col = manifest.target_column
        if target_col not in df.columns:
            if len(df.columns) > 0:
                target_col = df.columns[-1]
            else:
                raise ValueError(f"Target column {manifest.target_column} not found in dataset and dataset is empty.")
            
        X = df.drop(columns=[target_col])
        # Keep only numeric columns for scikit-learn estimators
        X = X.select_dtypes(include=['number'])
        if X.empty:
            # Fallback to original features if no numeric features are found
            X = df.drop(columns=[target_col])
            
        y = df[target_col]
        
        # Dynamically correct the task type if there is a mismatch with the target values
        unique_vals = y.dropna().unique()
        is_numeric = pd.api.types.is_numeric_dtype(y)
        
        task = manifest.task
        candidate_models = manifest.candidate_models
        
        if is_numeric and len(unique_vals) > 10:
            task = "Regression"
            new_models = []
            for m in candidate_models:
                m_lower = m.lower()
                if "lr" in m_lower:
                    new_models.append("lr")
                elif "rf" in m_lower:
                    new_models.append("rf_reg")
                else:
                    new_models.append(m)
            candidate_models = new_models
        elif len(unique_vals) <= 20:
            if task == "Regression":
                task = "Binary Classification" if len(unique_vals) == 2 else "Multi-class Classification"
                new_models = []
                for m in candidate_models:
                    m_lower = m.lower()
                    if m_lower == "lr":
                        new_models.append("lr_clf")
                    elif m_lower == "rf_reg":
                        new_models.append("rf_clf")
                    else:
                        new_models.append(m)
                candidate_models = new_models
                
        
        manifest.task = task
        manifest.candidate_models = candidate_models
        
        # Label encode target if classification to ensure y_true and y_pred have matching integer type
        if "Classification" in task:
            from sklearn.preprocessing import LabelEncoder
            le = LabelEncoder()
            y = pd.Series(le.fit_transform(y.fillna(y.mode()[0] if not y.mode().empty else 0)), index=y.index)
        
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
        if not leaderboard:
            # Gather training errors for more descriptive feedback
            errors = [res.get("error", "Unknown error") for res in results if res.get("status") == "FAILED"]
            err_msg = "; ".join(errors) if errors else "No successful candidate models"
            raise ValueError(f"No AutoML models trained successfully: {err_msg}")
            
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
