import pandas as pd
import numpy as np
from scipy import stats
from backend.engine.core.base_operation import BaseOperation

class ZScoreRemoval(BaseOperation):
    """
    Removes rows containing outliers in the specified columns based on the Z-Score method.
    Typically assumes a normal distribution.
    """
    def __init__(self, target_columns=None, threshold=3.0):
        super().__init__()
        self.target_columns = target_columns
        self.threshold = threshold
        
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
        
        # Calculate z-scores, handling NaNs
        z_scores = np.abs(stats.zscore(df[cols_to_process], nan_policy='omit'))
        outliers = (z_scores > self.threshold).any(axis=1)
        outlier_count = outliers.sum()
        
        self.log_info(f"Found {outlier_count} rows with outliers across {len(cols_to_process)} columns using Z-Score threshold {self.threshold}.")
        return {"outlier_rows_before": int(outlier_count), "columns": list(cols_to_process)}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        cols_to_process = self.target_columns if self.target_columns else df.select_dtypes(include='number').columns
        
        z_scores = np.abs(stats.zscore(df[cols_to_process], nan_policy='omit'))
        outliers = (z_scores > self.threshold).any(axis=1)
        df_clean = df[~outliers].copy()
        
        self.log_info(f"Removed {outliers.sum()} rows containing outliers.")
        return df_clean
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        if len(df_after) == 0 and len(df_before) > 0:
            self.log_warning("Verification failed: Z-Score removal deleted all rows.")
            return False
        self.log_info(f"Verification passed: dataset size reduced from {len(df_before)} to {len(df_after)} rows.")
        return True
