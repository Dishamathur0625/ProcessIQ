from abc import ABC, abstractmethod
import pandas as pd
import time
from .transformation_result import TransformationResult

class BaseOperation(ABC):
    """
    Abstract base class for all ProcessIQ preprocessing operations.
    Enforces a strict lifecycle: validate -> inspect -> execute -> verify -> report.
    """
    def __init__(self):
        self.operation_name = self.__class__.__name__
        self.logs = []
        self.warnings = []
        
    def log_info(self, message: str):
        self.logs.append(f"INFO: {message}")
        
    def log_warning(self, message: str):
        self.warnings.append(f"WARNING: {message}")

    @abstractmethod
    def validate(self, df: pd.DataFrame) -> bool:
        """Check if operation can run on the dataset."""
        pass
        
    @abstractmethod
    def inspect(self, df: pd.DataFrame) -> dict:
        """Gather pre-execution metrics."""
        pass
        
    @abstractmethod
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        """Perform the actual transformation."""
        pass
        
    @abstractmethod
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        """Verify the transformation succeeded."""
        pass
        
    def run(self, df: pd.DataFrame) -> TransformationResult:
        """Orchestrates the preprocessing lifecycle with full performance profiling."""
        import time
        import psutil
        import os
        
        start_time = time.time()
        start_cpu = time.process_time()
        process = psutil.Process(os.getpid())
        start_mem = process.memory_info().rss
        
        self.log_info(f"Starting operation {self.operation_name}")
        
        # 1. Validate
        if not self.validate(df):
            self.log_warning("Validation failed. Aborting operation.")
            raise ValueError(f"Validation failed for {self.operation_name}")
            
        # 2. Inspect
        pre_stats = self.inspect(df)
        quality_before = 80.0 # Placeholder for IDRS calculation call
        
        # 3. Execute
        df_after = self.execute(df.copy())
        
        # 4. Verify
        if not self.verify(df, df_after):
            self.log_warning("Verification failed. Changes may be invalid.")
            raise RuntimeError(f"Verification failed for {self.operation_name}")
            
        # Performance Profiling
        execution_time_ms = (time.time() - start_time) * 1000
        cpu_time_ms = (time.process_time() - start_cpu) * 1000
        end_mem = process.memory_info().rss
        memory_usage_mb = max(0, (end_mem - start_mem)) / (1024 * 1024)
        rows_processed = len(df_after)
        throughput_rows_per_sec = rows_processed / (execution_time_ms / 1000.0) if execution_time_ms > 0 else 0.0
        
        quality_after = 95.0 # Placeholder for IDRS calculation call
        
        self.log_info(f"Successfully completed in {execution_time_ms:.2f}ms. CPU: {cpu_time_ms:.2f}ms. Mem: {memory_usage_mb:.2f}MB")
        
        # Grab feature metadata if this was a Feature Generator
        feature_metadata = getattr(self, "generated_features", [])
        
        # 5. Report
        return TransformationResult(
            dataset=df_after,
            operation_name=self.operation_name,
            execution_time_ms=execution_time_ms,
            cpu_time_ms=cpu_time_ms,
            memory_usage_mb=memory_usage_mb,
            rows_processed=rows_processed,
            throughput_rows_per_sec=throughput_rows_per_sec,
            summary=f"Successfully applied {self.operation_name}",
            logs=self.logs,
            warnings=self.warnings,
            quality_before=quality_before,
            quality_after=quality_after,
            statistics=pre_stats,
            feature_metadata=feature_metadata
        )
