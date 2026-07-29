from sqlalchemy import Column, String, DateTime, JSON, Float
from datetime import datetime
from backend.core.database import Base
import uuid

class PipelineJob(Base):
    __tablename__ = "pipeline_jobs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    dataset_id = Column(String, index=True)
    status = Column(String, default="QUEUED")  # QUEUED, RUNNING, COMPLETED, FAILED
    
    # E.g. {"validation": true, "cleaning": true}
    configuration = Column(JSON, default=dict)
    
    # Store metrics from execution
    execution_time_ms = Column(Float, nullable=True)
    memory_usage_mb = Column(Float, nullable=True)
    error_message = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
