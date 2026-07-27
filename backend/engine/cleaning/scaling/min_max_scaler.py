import pandas as pd
from sklearn.preprocessing import MinMaxScaler as SklearnMinMaxScaler
from backend.engine.core.base_operation import BaseOperation

class MinMaxScaler(BaseOperation):
    """
    Scales numerical features to a given range, typically [0, 1].
    Preserves the shape of the original distribution.
    """
    def __init__(self, target_columns=None):
        super().__init__()
        self.target_columns = target_columns
        self.scaler = SklearnMinMaxScaler()
        
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
        self.log_info(f"MinMax scaling will be applied to {len(cols_to_process)} columns.")
        return {"columns": list(cols_to_process)}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        cols_to_process = self.target_columns if self.target_columns else df.select_dtypes(include='number').columns
        if len(cols_to_process) > 0:
            df[cols_to_process] = self.scaler.fit_transform(df[cols_to_process])
            self.log_info("Successfully applied MinMax scaling.")
        return df
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        cols_to_process = self.target_columns if self.target_columns else df_after.select_dtypes(include='number').columns
        if len(cols_to_process) > 0:
            max_vals = df_after[cols_to_process].max()
            min_vals = df_after[cols_to_process].min()
            
            # Allow minor floating point inaccuracies
            if (max_vals > 1.0001).any() or (min_vals < -0.0001).any():
                self.log_warning("Verification failed: values are outside the [0,1] range.")
                return False
                
        self.log_info("Verification passed: all targeted features are scaled between 0 and 1.")
        return True
