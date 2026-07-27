from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from backend.core.database import Base
import datetime
import uuid

def generate_uuid():
    return str(uuid.uuid4())

class DatasetVersion(Base):
    __tablename__ = "dataset_versions"

    id = Column(String, primary_key=True, default=generate_uuid)
    project_id = Column(String, index=True)
    parent_version_id = Column(String, ForeignKey("dataset_versions.id"), nullable=True)
    
    storage_path = Column(String, nullable=False)
    operation_applied = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Relationship to parent and children
    children = relationship("DatasetVersion", backref="parent", remote_side=[id])
    
class TransformationReport(Base):
    __tablename__ = "transformation_reports"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    dataset_version_id = Column(String, ForeignKey("dataset_versions.id"))
    
    operation_name = Column(String)
    execution_time_ms = Column(Float)
    quality_before = Column(Float)
    quality_after = Column(Float)
    
    metadata_json = Column(JSON) # Stores the full TransformationResult dump
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
