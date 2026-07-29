from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from backend.core.database import Base

class TrainingPlan(Base):
    __tablename__ = "training_plans"
    
    id = Column(String, primary_key=True, index=True)
    dataset_fingerprint = Column(String, index=True)
    job_id = Column(String, ForeignKey("processing_jobs.id"))
    
    task = Column(String, nullable=False)
    target_column = Column(String, nullable=False)
    
    # Metadata for Versioning and Lineage
    planner_version = Column(String)
    engine_version = Column(String)
    pipeline_version = Column(String)
    feature_set_version = Column(String)
    
    # Full serialized JSON of the training plan
    plan_config = Column(JSON)
    
    # Tracking for Phase 14
    status = Column(String, default="PLANNED")
    automl_run_id = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class TrainingSession(Base):
    __tablename__ = "training_sessions"
    
    id = Column(String, primary_key=True, index=True)
    job_id = Column(String, ForeignKey("processing_jobs.id"))
    training_plan_id = Column(String, ForeignKey("training_plans.id"))
    dataset_fingerprint = Column(String, index=True)
    
    status = Column(String, default="RUNNING") # RUNNING, COMPLETED, FAILED
    execution_manifest = Column(JSON)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    models = relationship("MLModel", back_populates="session")

class MLModel(Base):
    __tablename__ = "ml_models"
    
    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("training_sessions.id"))
    training_plan_id = Column(String, ForeignKey("training_plans.id"))
    
    dataset_fingerprint = Column(String)
    planner_version = Column(String)
    engine_version = Column(String)
    
    task = Column(String)
    algorithm = Column(String)
    
    random_seed = Column(String)
    hyperparameters = Column(JSON)
    metrics = Column(JSON)
    status = Column(String)
    
    training_duration_sec = Column(String)
    artifact_locations = Column(JSON) # pointers to model.joblib, explainer plots
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    session = relationship("TrainingSession", back_populates="models")
