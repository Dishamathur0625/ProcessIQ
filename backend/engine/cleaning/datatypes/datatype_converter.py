import pandas as pd
from backend.engine.core.base_operation import BaseOperation

class DatatypeConverter(BaseOperation):
    """
    Attempts to coerce target columns into numeric or datetime datatypes.
    """
    def __init__(self, target_columns: list, target_type: str = 'numeric'):
        super().__init__()
        self.target_columns = target_columns
        self.target_type = target_type # 'numeric' or 'datetime'
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty or not self.target_columns:
            return False
        for col in self.target_columns:
            if col not in df.columns:
                self.log_warning(f"Target column {col} not found in dataset.")
                return False
        if self.target_type not in ['numeric', 'datetime']:
            self.log_warning("Target type must be 'numeric' or 'datetime'.")
            return False
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        self.log_info(f"Will attempt to convert {len(self.target_columns)} columns to {self.target_type}.")
        return {"columns": self.target_columns, "target_type": self.target_type}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        for col in self.target_columns:
            if self.target_type == 'numeric':
                df[col] = pd.to_numeric(df[col], errors='coerce')
            elif self.target_type == 'datetime':
                df[col] = pd.to_datetime(df[col], errors='coerce')
                
        self.log_info(f"Conversion complete. Note: Unparseable values were coerced to NaNs.")
        return df
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        # Check if the columns are actually of the intended type
        for col in self.target_columns:
            if self.target_type == 'numeric' and not pd.api.types.is_numeric_dtype(df_after[col]):
                self.log_warning(f"Verification failed: Column {col} is not numeric.")
                return False
            if self.target_type == 'datetime' and not pd.api.types.is_datetime64_any_dtype(df_after[col]):
                self.log_warning(f"Verification failed: Column {col} is not datetime.")
                return False
        self.log_info("Verification passed: all target columns converted successfully.")
        return True
