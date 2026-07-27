import pandas as pd
from backend.engine.core.base_operation import BaseOperation

class ForwardFill(BaseOperation):
    """
    Imputes missing values using forward fill (ffill).
    Highly recommended for time-series and sensor data where the last known value is often the most accurate estimate.
    """
    def __init__(self, target_columns=None):
        super().__init__()
        self.target_columns = target_columns
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty:
            return False
        if self.target_columns:
            for col in self.target_columns:
                if col not in df.columns:
                    self.log_warning(f"Target column {col} not found in dataset.")
                    return False
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        cols_to_process = self.target_columns if self.target_columns else df.columns
        missing = df[cols_to_process].isna().sum()
        total_missing = missing.sum()
        self.log_info(f"Found {total_missing} missing values to impute across {len(cols_to_process)} columns.")
        return {"missing_before": int(total_missing), "columns": list(cols_to_process)}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        cols_to_process = self.target_columns if self.target_columns else df.columns
        df[cols_to_process] = df[cols_to_process].ffill()
        self.log_info(f"Forward fill applied to {len(cols_to_process)} columns.")
        return df
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        cols_to_process = self.target_columns if self.target_columns else df_after.columns
        remaining_missing = df_after[cols_to_process].isna().sum().sum()
        if remaining_missing > 0:
            # ffill can leave NaNs if they are at the very beginning of the dataset
            self.log_warning(f"Verification flag: {remaining_missing} missing values remain (likely at the start of series).")
        else:
            self.log_info("Verification passed: 0 missing values remain.")
        return True
