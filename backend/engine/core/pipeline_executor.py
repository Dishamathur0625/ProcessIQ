import pandas as pd
from typing import List, Dict, Any, Type
from backend.engine.core.base_operation import BaseOperation
from backend.engine.core.audit_engine import AuditEngine
from backend.engine.core.version_graph import DatasetVersionGraph
from backend.engine.profiling.dataset_profiler import DatasetProfiler

class PipelineExecutor:
    """
    Executes a chain of BaseOperations on a dataset in a deterministic manner.
    Maintains the version graph, records audits, and automatically re-profiles the dataset.
    """
    def __init__(self, df: pd.DataFrame, user_id: str = "system"):
        self.df = df.copy()
        self.user_id = user_id
        self.version_graph = DatasetVersionGraph()
        self.audit_trail: List[Dict[str, Any]] = []
        self.feature_metadata_registry: List[Any] = []
        
        # Profile initial state
        initial_profile = self._profile_current_state()
        self.version_graph.add_initial_version(initial_profile["fingerprint"], initial_profile["quality_scores"])
        self.initial_quality = initial_profile["quality_scores"]
        self.final_quality = None
        
    def _profile_current_state(self) -> Dict[str, Any]:
        profiler = DatasetProfiler(self.df)
        return profiler.execute_profiling_pipeline()
        
    def execute_chain(self, operations: List[BaseOperation]) -> Dict[str, Any]:
        """
        Executes a list of operations sequentially.
        """
        for op in operations:
            # Run the operation
            result = op.run(self.df)
            
            # Extract parameters for auditing (hacky for now, real system would serialize the object config)
            params = getattr(op, "target_columns", "all")
            
            # Generate immutable audit hash
            audit_record = AuditEngine.generate_audit_record(
                user_id=self.user_id,
                dataset_version_id=self.version_graph.current_version_id,
                result=result,
                parameters={"target_columns": params}
            )
            self.audit_trail.append(audit_record)
            
            # Update the dataset
            self.df = result.dataset
            
            # Re-profile to get new deterministic state
            new_profile = self._profile_current_state()
            
            # Record transition in the version graph
            self.version_graph.record_transition(
                new_fingerprint=new_profile["fingerprint"],
                new_quality_scores=new_profile["quality_scores"],
                operation_name=result.operation_name,
                audit_hash=audit_record["audit_hash"]
            )
            
            # Aggregate generated feature metadata
            if result.feature_metadata:
                self.feature_metadata_registry.extend(result.feature_metadata)
                
            self.final_quality = new_profile["quality_scores"]
            
        return {
            "final_dataset": self.df,
            "lineage": self.version_graph.get_lineage(),
            "audit_trail": self.audit_trail,
            "feature_metadata": self.feature_metadata_registry,
            "initial_quality": self.initial_quality,
            "final_quality": self.final_quality
        }
