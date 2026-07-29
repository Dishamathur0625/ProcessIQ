from sqlalchemy import Column, String, DateTime, JSON
from datetime import datetime
from backend.core.database import Base
import uuid

class PipelineArtifact(Base):
    """
    Generic table to store metadata for all outputs related to a job:
    REPORT, VISUALIZATION, MANIFEST, AUDIT, BENCHMARK.
    """
    __tablename__ = "pipeline_artifacts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String, index=True)
    
    artifact_type = Column(String, index=True) # E.g., REPORT, VISUALIZATION, AUDIT
    name = Column(String) # E.g., "ieee_evaluation_report.md" or "quality_scores.json"
    
    # Path where the artifact is stored on disk
    file_path = Column(String, nullable=True)
    
    # Optional JSON content if the artifact is small enough to store in DB
    content_json = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
