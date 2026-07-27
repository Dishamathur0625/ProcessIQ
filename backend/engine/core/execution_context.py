from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import uuid

class ExecutionLineage(BaseModel):
    """
    Tracks the lineage of a dataset through the pipeline.
    Ensures rollback and full auditability for IEEE/industrial standards.
    """
    version_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    parent_version_id: Optional[str] = None
    dataset_id: str
    operations_applied: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    pipeline_id: Optional[str] = None
    
    def add_operation(self, operation_name: str):
        self.operations_applied.append(operation_name)
