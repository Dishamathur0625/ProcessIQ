import pandas as pd
import numpy as np
from typing import List
from backend.engine.features.base_feature_generator import BaseFeatureGenerator

class LogTransformGenerator(BaseFeatureGenerator):
    """
    Generates log transformations (log(1+x)) for numeric columns to handle skewness.
    """
    def __init__(self, target_columns: List[str]):
        super().__init__(target_columns)
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty or not self.target_columns:
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
        expected_features = len(self.target_columns)
        self.log_info(f"Will generate {expected_features} log transform features.")
        return {"expected_features": expected_features}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        df_new = df.copy()
        
        for col in self.target_columns:
            new_col_name = f"{col}_log1p"
            
            # log(1+x) is used to avoid -inf on 0.
            # Handle negative values by shifting if necessary, or just warn/NaN
            min_val = df_new[col].min()
            if min_val < 0:
                self.log_warning(f"Column {col} has negative values. Shifting to positive domain before log1p.")
                shift = abs(min_val)
                df_new[new_col_name] = np.log1p(df_new[col] + shift)
                formula = f"log1p({col} + {shift})"
            else:
                df_new[new_col_name] = np.log1p(df_new[col])
                formula = f"log1p({col})"
            
            self._create_metadata(
                new_feature_name=new_col_name,
                source_cols=[col],
                formula=formula
            )
            self.log_info(f"Generated {new_col_name}")
                
        return df_new
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        expected_features = len(self.target_columns)
        actual_new_features = len(df_after.columns) - len(df_before.columns)
        
        if actual_new_features != expected_features:
            self.log_warning(f"Verification failed: Expected {expected_features} new features, got {actual_new_features}.")
            return False
        return True
