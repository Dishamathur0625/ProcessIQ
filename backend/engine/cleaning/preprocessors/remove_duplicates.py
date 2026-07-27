import pandas as pd
from backend.engine.core.base_operation import BaseOperation

class RemoveDuplicates(BaseOperation):
    """
    Identifies and removes completely duplicated rows in the dataset.
    Implements the strict BaseOperation lifecycle.
    """
    def __init__(self):
        super().__init__()
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty:
            self.log_warning("Dataset is empty. Cannot process duplicates.")
            return False
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        duplicate_count = int(df.duplicated().sum())
        duplicate_percentage = (duplicate_count / len(df)) * 100 if len(df) > 0 else 0
        
        self.log_info(f"Found {duplicate_count} duplicate rows ({duplicate_percentage:.2f}%).")
        return {
            "duplicate_count_before": duplicate_count,
            "duplicate_percentage_before": duplicate_percentage
        }
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        self.log_info("Dropping duplicates...")
        df_clean = df.drop_duplicates()
        return df_clean
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        remaining_duplicates = df_after.duplicated().sum()
        if remaining_duplicates > 0:
            self.log_warning(f"Verification failed: {remaining_duplicates} duplicates remain.")
            return False
            
        rows_removed = len(df_before) - len(df_after)
        self.log_info(f"Verification passed: {rows_removed} rows were removed.")
        return True
