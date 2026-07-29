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
from backend.engine.reports.pipeline_report import PipelineReportGenerator
from backend.engine.visualization.spec_generator import VisualizationSpecGenerator

import time
import logging

logger = logging.getLogger(__name__)

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
        
        # 3. Dynamic Pipeline configuration (Hardcoded for demo, would parse config here)
        ops = []
        if configuration.get("cleaning"):
            # Example operation: would dynamically map via OperationRegistry in a real scenario
            numeric_cols = df.select_dtypes(include='number').columns.tolist()
            if numeric_cols:
                ops.append(MeanImputation(target_columns=numeric_cols))
                
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
            report = PipelineReportGenerator.generate_full_report(result)
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
            # Quick hack to get visualizations for first numeric column
            numeric_cols = final_df.select_dtypes(include='number').columns.tolist()
            if numeric_cols:
                viz_json = VisualizationSpecGenerator.generate_distribution_plot(final_df, numeric_cols[0])
                art_viz = PipelineArtifact(
                    job_id=job_id,
                    artifact_type="VISUALIZATION",
                    name=f"dist_{numeric_cols[0]}",
                    content_json=viz_json
                )
                db.add(art_viz)
                
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
