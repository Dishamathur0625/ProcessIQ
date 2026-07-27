import json
import hashlib
from typing import Dict, Any
from datetime import datetime
from backend.engine.core.transformation_result import TransformationResult

class AuditEngine:
    """
    Generates immutable audit records for every preprocessing operation.
    Ensures absolute traceability for enterprise compliance and research reproducibility.
    """
    
    @staticmethod
    def generate_audit_record(
        user_id: str, 
        dataset_version_id: str, 
        result: TransformationResult, 
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        
        record = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "user_id": user_id,
            "dataset_version_id": dataset_version_id,
            "operation": result.operation_name,
            "parameters": parameters,
            "execution_metrics": {
                "execution_time_ms": result.execution_time_ms,
                "cpu_time_ms": result.cpu_time_ms,
                "memory_usage_mb": result.memory_usage_mb,
                "rows_processed": result.rows_processed,
                "throughput_rows_per_sec": result.throughput_rows_per_sec
            },
            "quality_metrics": {
                "quality_before": result.quality_before,
                "quality_after": result.quality_after
            },
            "warnings": result.warnings
        }
        
        # Create an immutable deterministic hash of the mathematical operation
        deterministic_record = {
            "dataset_version_id": dataset_version_id,
            "operation": result.operation_name,
            "parameters": parameters
        }
        record_string = json.dumps(deterministic_record, sort_keys=True)
        record_hash = hashlib.sha256(record_string.encode('utf-8')).hexdigest()
        record["audit_hash"] = record_hash
        
        return record
