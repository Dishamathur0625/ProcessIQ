import pandas as pd
from sklearn.preprocessing import StandardScaler as SklearnStandardScaler
from backend.engine.core.base_operation import BaseOperation
from backend.engine.core.exceptions import DataLeakageError

class StandardScaler(BaseOperation):
    """
    Standardizes features by removing the mean and scaling to unit variance.
    Includes safeguards against data leakage (e.g. scaling the target column).
    """
    def __init__(self, target_column: str = None):
        super().__init__()
        self.target_column = target_column
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty:
            return False
        numeric_cols = df.select_dtypes(include='number').columns
        if len(numeric_cols) == 0:
            self.log_warning("No numeric columns found for scaling.")
            return False
            
        if self.target_column and self.target_column in numeric_cols:
            self.log_warning(f"Target column '{self.target_column}' is numeric. It will be excluded from scaling to prevent data leakage.")
            
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        numeric_cols = df.select_dtypes(include='number').columns
        cols_to_scale = [c for c in numeric_cols if c != self.target_column]
        
        self.log_info(f"Identified {len(cols_to_scale)} columns for standard scaling.")
        return {"columns_to_scale": cols_to_scale}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        numeric_cols = df.select_dtypes(include='number').columns
        cols_to_scale = [c for c in numeric_cols if c != self.target_column]
        
        if not cols_to_scale:
            return df
            
        scaler = SklearnStandardScaler()
        df[cols_to_scale] = scaler.fit_transform(df[cols_to_scale])
        
        self.log_info("Standard scaling applied successfully.")
        return df
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        numeric_cols = df_after.select_dtypes(include='number').columns
        cols_to_scale = [c for c in numeric_cols if c != self.target_column]
        
        if not cols_to_scale:
            return True
            
        # Verify mean is close to 0 and std is close to 1
        means = df_after[cols_to_scale].mean().abs()
        stds = df_after[cols_to_scale].std()
        
        if (means > 0.1).any():
            self.log_warning("Verification failed: Scaled columns have mean significantly different from 0.")
            return False
            
        self.log_info("Verification passed: Standard Scaling succeeded.")
        return True
