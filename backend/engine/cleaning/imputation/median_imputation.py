import pandas as pd
from backend.engine.core.base_operation import BaseOperation

class MedianImputation(BaseOperation):
    """
    Imputes missing values in numeric columns using the median.
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
        cols_to_process = self.target_columns if self.target_columns else df.select_dtypes(include='number').columns
        missing = df[cols_to_process].isna().sum()
        total_missing = missing.sum()
        self.log_info(f"Found {total_missing} missing values to impute across {len(cols_to_process)} columns.")
        return {"missing_before": int(total_missing), "columns": list(cols_to_process)}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        cols_to_process = self.target_columns if self.target_columns else df.select_dtypes(include='number').columns
        for col in cols_to_process:
            median_val = df[col].median()
            df[col] = df[col].fillna(median_val)
            self.log_info(f"Imputed {col} with median value {median_val:.4f}")
        return df
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        cols_to_process = self.target_columns if self.target_columns else df_after.select_dtypes(include='number').columns
        remaining_missing = df_after[cols_to_process].isna().sum().sum()
        if remaining_missing > 0:
            self.log_warning(f"Verification failed: {remaining_missing} missing values remain.")
            return False
        self.log_info("Verification passed: 0 missing values remain in target columns.")
        return True
