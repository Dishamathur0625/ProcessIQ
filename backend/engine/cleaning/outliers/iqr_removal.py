import pandas as pd
from backend.engine.core.base_operation import BaseOperation

class IQRRemoval(BaseOperation):
    """
    Removes rows containing outliers in the specified columns based on the Interquartile Range (IQR) method.
    """
    def __init__(self, target_columns=None, multiplier=1.5):
        super().__init__()
        self.target_columns = target_columns
        self.multiplier = multiplier
        
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
        
        Q1 = df[cols_to_process].quantile(0.25)
        Q3 = df[cols_to_process].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - self.multiplier * IQR
        upper_bound = Q3 + self.multiplier * IQR
        
        outliers = ((df[cols_to_process] < lower_bound) | (df[cols_to_process] > upper_bound)).any(axis=1)
        outlier_count = outliers.sum()
        
        self.log_info(f"Found {outlier_count} rows with outliers across {len(cols_to_process)} columns using IQR multiplier {self.multiplier}.")
        return {"outlier_rows_before": int(outlier_count), "columns": list(cols_to_process)}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        cols_to_process = self.target_columns if self.target_columns else df.select_dtypes(include='number').columns
        
        Q1 = df[cols_to_process].quantile(0.25)
        Q3 = df[cols_to_process].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - self.multiplier * IQR
        upper_bound = Q3 + self.multiplier * IQR
        
        outliers = ((df[cols_to_process] < lower_bound) | (df[cols_to_process] > upper_bound)).any(axis=1)
        df_clean = df[~outliers].copy()
        
        self.log_info(f"Removed {outliers.sum()} rows containing outliers.")
        return df_clean
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        if len(df_after) == 0 and len(df_before) > 0:
            self.log_warning("Verification failed: IQR removal deleted all rows.")
            return False
        self.log_info(f"Verification passed: dataset size reduced from {len(df_before)} to {len(df_after)} rows.")
        return True
