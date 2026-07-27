import pandas as pd
import numpy as np
from typing import List
from backend.engine.features.base_feature_generator import BaseFeatureGenerator

class CyclicEncoderGenerator(BaseFeatureGenerator):
    """
    Generates Cyclic Encoded features (sin/cos) for periodic numeric columns (e.g., hour, month).
    """
    def __init__(self, target_columns: List[str], max_vals: List[float]):
        super().__init__(target_columns)
        self.max_vals = max_vals # the maximum value of the cycle (e.g. 24 for hour, 12 for month)
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty or not self.target_columns:
            return False
        if len(self.target_columns) != len(self.max_vals):
            self.log_warning("Must provide a max_val for each target column.")
            return False
        for col in self.target_columns:
            if col not in df.columns:
                self.log_warning(f"Target column {col} not found in dataset.")
                return False
            if not pd.api.types.is_numeric_dtype(df[col]):
                self.log_warning(f"Target column {col} is not numeric.")
                return False
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        expected_features = len(self.target_columns) * 2 # sin and cos
        self.log_info(f"Will generate {expected_features} Cyclic Encoded features.")
        return {"expected_features": expected_features}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        df_new = df.copy()
        
        for col, max_val in zip(self.target_columns, self.max_vals):
            sin_col = f"{col}_sin"
            cos_col = f"{col}_cos"
            
            df_new[sin_col] = np.sin(2 * np.pi * df_new[col] / max_val)
            df_new[cos_col] = np.cos(2 * np.pi * df_new[col] / max_val)
            
            self._create_metadata(
                new_feature_name=sin_col,
                source_cols=[col],
                formula=f"sin(2pi*{col}/{max_val})"
            )
            self._create_metadata(
                new_feature_name=cos_col,
                source_cols=[col],
                formula=f"cos(2pi*{col}/{max_val})"
            )
            self.log_info(f"Generated {sin_col} and {cos_col}")
                
        return df_new
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        expected_features = len(self.target_columns) * 2
        actual_new_features = len(df_after.columns) - len(df_before.columns)
        
        if actual_new_features != expected_features:
            self.log_warning(f"Verification failed: Expected {expected_features} new features, got {actual_new_features}.")
            return False
        return True
