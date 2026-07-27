from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class TransformationResult(BaseModel):
    """
    Standardized return object for every preprocessing operation in ProcessIQ.
    Ensures rich metadata is always passed back to the UI and LLM.
    """
    # The dataset itself won't be serialized to JSON, it's kept in memory for the pipeline
    dataset: Any 
    operation_name: str
    
    # Performance Profiling Metrics
    execution_time_ms: float
    cpu_time_ms: Optional[float] = None
    memory_usage_mb: Optional[float] = None
    rows_processed: Optional[int] = None
    throughput_rows_per_sec: Optional[float] = None
    
    # Standard Metadata
    summary: str
    logs: List[str]
    warnings: List[str]
    quality_before: float
    quality_after: float
    statistics: Dict[str, Any]
    recommendations: Optional[List[str]] = []
    
    # Feature Engineering metadata (optional)
    feature_metadata: Optional[List[Any]] = []
