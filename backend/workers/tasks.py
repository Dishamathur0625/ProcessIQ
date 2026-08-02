import os
import pandas as pd
from datetime import datetime
from backend.workers.celery_app import celery_app
from backend.core.database import SessionLocal
from backend.db.models.job import PipelineJob
from backend.db.models.artifact import PipelineArtifact
from backend.storage.file_manager import FileManager
from backend.engine.core.pipeline_executor import PipelineExecutor
from backend.engine.cleaning.imputation.mean_imputation import MeanImputation
from backend.engine.cleaning.preprocessors.remove_duplicates import RemoveDuplicates
from backend.engine.cleaning.scaling.min_max_scaler import MinMaxScaler
from backend.engine.features.categorical.one_hot_generator import OneHotEncoderGenerator
from backend.engine.reports.pipeline_report import PipelineReportGenerator
from backend.engine.visualization.spec_generator import VisualizationSpecificationGenerator

import time
import logging
import json

logger = logging.getLogger(__name__)

# Helper to dynamically generate metadata artifacts for the Prediction Planner
def generate_metadata_artifacts(df: pd.DataFrame, job_id: str):
    import re
    features = {}
    row_count = len(df)
    
    for col in df.columns:
        col_lower = col.lower()
        is_id = col_lower == "id" or col_lower.endswith("_id") or (df[col].nunique() == row_count and row_count > 10)
        
        # Simple datetime detection
        is_dt = pd.api.types.is_datetime64_any_dtype(df[col]) or "date" in col_lower or "time" in col_lower
        
        # Infer type
        if is_dt:
            inferred = "datetime"
        elif pd.api.types.is_numeric_dtype(df[col]):
            if pd.api.types.is_integer_dtype(df[col]):
                inferred = "integer"
            else:
                inferred = "float"
        elif df[col].nunique() < 20:
            inferred = "categorical"
        else:
            inferred = "string"
            
        features[col] = {
            "inferred_type": inferred,
            "unique_count": int(df[col].nunique()),
            "missing_ratio": float(df[col].isna().mean()),
            "is_identifier": bool(is_id),
            "is_datetime": bool(is_dt)
        }
        
    feature_metadata = {
        "row_count": row_count,
        "features": features
    }
    
    # Generate warnings for quality report
    warnings = []
    if row_count < 100:
        warnings.append("Tiny dataset detected. Machine learning models may overfit.")
    for col, meta in features.items():
        if meta["missing_ratio"] > 0.0:
            warnings.append(f"Column {col} has {meta['missing_ratio']*100:.1f}% missing values.")
            
    quality_report = {
        "warnings": warnings
    }
    
    # Generate fingerprint
    from backend.engine.profiling.fingerprint import DatasetFingerprint
    fingerprint_val = DatasetFingerprint.generate(df)
    fingerprint = {
        "dataset_fingerprint": fingerprint_val
    }
    
    return feature_metadata, quality_report, fingerprint


@celery_app.task(bind=True)
def execute_pipeline_task(self, job_id: str, configuration: dict):
    db = SessionLocal()
    job = db.query(PipelineJob).filter(PipelineJob.id == job_id).first()
    if not job:
        db.close()
        return "Job not found"
        
    job.status = "RUNNING"
    db.commit()
    
    start_time = time.time()
    
    try:
        from backend.services.storage.factory import StorageFactory
        from backend.core.config import settings
        import io
        
        storage = StorageFactory.get_backend()
        
        # 1. Load dataset
        dataset_path = f"{job_id}/dataset.csv"
        dataset_bytes = storage.download(settings.SUPABASE_BUCKET_DATASETS, dataset_path)
        df = pd.read_csv(io.BytesIO(dataset_bytes))
        
        # 2. Setup Executor
        executor = PipelineExecutor(df)
        
        # 3. Dynamic Pipeline configuration
        ops = []
        
        is_plant_data = False
        from backend.engine.cleaning.preprocessors.plant_data_aligner import PlantDataAligner
        plant_aligner = PlantDataAligner()
        if plant_aligner.validate(df):
            is_plant_data = True
            ops.append(plant_aligner)
            
        if configuration.get("cleaning"):
            ops.append(RemoveDuplicates())
            ops.append(MeanImputation())
                
        if configuration.get("feature_engineering"):
            # Skip scaling for plant data as users want original values
            if not is_plant_data:
                ops.append(MinMaxScaler())
                
            # Categorical encoding shouldn't be strictly configured based on initial df
            # because the dataframe might change. We'll use OneHotEncoderGenerator with no targets
            # wait, OneHotEncoderGenerator requires target_columns if we want to restrict to low_card
            # I will keep the explicit logic but we should evaluate it AFTER PlantDataAligner if possible
            # Actually, I'll let OneHotEncoderGenerator handle it dynamically if possible. Let me check its code.
            # I will just keep the original logic for categorical for now, as PlantDataAligner doesn't create new categorical columns, it only creates numeric columns.
            cat_cols = [col for col in df.columns if df[col].dtype == 'object' or df[col].dtype == 'category']
            low_card_cats = [col for col in cat_cols if 1 < df[col].nunique() <= 20]
            if low_card_cats:
                ops.append(OneHotEncoderGenerator(target_columns=low_card_cats))
                
        # 4. Execute Pipeline
        result = executor.execute_chain(ops)
        final_df = result["final_dataset"]
        
        # 5. Save Processed Dataset
        csv_str = final_df.to_csv(index=False)
        processed_path = f"{job_id}/processed_dataset.csv"
        storage.upload(settings.SUPABASE_BUCKET_PROCESSED, processed_path, io.BytesIO(csv_str.encode('utf-8')))
        
        job.status = "GENERATING_REPORTS"
        db.commit()
        
        # 6. Generate Reports
        if configuration.get("reports"):
            report = PipelineReportGenerator.generate_markdown(result)
            report_path = f"{job_id}/pipeline_report.md"
            storage.upload(settings.SUPABASE_BUCKET_REPORTS, report_path, io.BytesIO(report.encode('utf-8')))
            
            art_report = PipelineArtifact(
                job_id=job_id,
                artifact_type="REPORT",
                name="pipeline_report.md",
                file_path=report_path
            )
            db.add(art_report)
            
        job.status = "GENERATING_VISUALIZATIONS"
        db.commit()
        
        # 7. Generate Visualizations
        if configuration.get("visualization"):
            # We want to generate an entire suite of visualizations for the frontend
            # including correlations, distributions, and scatterplots.
            # If the user specified a target variable for AutoML in configuration, we'd use it, 
            # otherwise we just generate a general suite.
            target = configuration.get("automl_target") # (if available)
            viz_suite = VisualizationSpecificationGenerator.generate_suite_for_dataset(final_df, target_variable=target)
            
            # Convert list of pydantic models to dicts
            viz_json = [spec.dict() for spec in viz_suite]
            
            art_viz = PipelineArtifact(
                job_id=job_id,
                artifact_type="VISUALIZATION",
                name="visualizations_suite",
                content_json=viz_json
            )
            db.add(art_viz)
                
        # 7.5 Save Feature Metadata, Quality Report, Fingerprint for the Prediction Planner
        feature_metadata, quality_report, fingerprint = generate_metadata_artifacts(final_df, job_id)
        
        metadata_path = f"{job_id}/feature_metadata.json"
        quality_path = f"{job_id}/quality_report.json"
        fingerprint_path = f"{job_id}/fingerprint.json"
        
        storage.upload(settings.SUPABASE_BUCKET_ARTIFACTS, metadata_path, io.BytesIO(json.dumps(feature_metadata).encode('utf-8')))
        storage.upload(settings.SUPABASE_BUCKET_REPORTS, quality_path, io.BytesIO(json.dumps(quality_report).encode('utf-8')))
        storage.upload(settings.SUPABASE_BUCKET_ARTIFACTS, fingerprint_path, io.BytesIO(json.dumps(fingerprint).encode('utf-8')))
        
        art_meta = PipelineArtifact(
            job_id=job_id,
            artifact_type="feature_metadata",
            name="feature_metadata.json",
            content_json=feature_metadata
        )
        art_quality = PipelineArtifact(
            job_id=job_id,
            artifact_type="quality_report",
            name="quality_report.json",
            content_json=quality_report
        )
        art_fingerprint = PipelineArtifact(
            job_id=job_id,
            artifact_type="fingerprint",
            name="fingerprint.json",
            content_json=fingerprint
        )
        db.add(art_meta)
        db.add(art_quality)
        db.add(art_fingerprint)
                
        # 8. Mark Completed
        end_time = time.time()
        job.status = "COMPLETED"
        job.completed_at = datetime.utcnow()
        job.execution_time_ms = (end_time - start_time) * 1000
        
        # Save Audit Trail
        audit_art = PipelineArtifact(
            job_id=job_id,
            artifact_type="AUDIT",
            name="audit_trail.json",
            content_json={"audit_trail": result["audit_trail"]}
        )
        db.add(audit_art)
        
        db.commit()
        
        logger.info(f"Job {job_id} completed successfully in {job.execution_time_ms}ms")
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {str(e)}")
        job.status = "FAILED"
        job.error_message = str(e)
        job.completed_at = datetime.utcnow()
        db.commit()
        
    finally:
        db.close()
