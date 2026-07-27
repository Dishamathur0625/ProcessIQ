import pandas as pd
from typing import List
from backend.engine.features.base_feature_generator import BaseFeatureGenerator

class LagFeatureGenerator(BaseFeatureGenerator):
    """
    Generates time-series lag features (e.g., Temperature_lag_1).
    """
    def __init__(self, target_columns: List[str], lags: List[int] = [1]):
        super().__init__(target_columns)
        self.lags = lags
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty or not self.target_columns:
            return False
        for col in self.target_columns:
            if col not in df.columns:
                self.log_warning(f"Target column {col} not found in dataset.")
                return False
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        expected_features = len(self.target_columns) * len(self.lags)
        self.log_info(f"Will generate {expected_features} lag features.")
        return {"expected_features": expected_features, "lags": self.lags}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        df_new = df.copy()
        
        for col in self.target_columns:
            for lag in self.lags:
                new_col_name = f"{col}_lag_{lag}"
                df_new[new_col_name] = df_new[col].shift(lag)
                
                # Record Feature Metadata
                self._create_metadata(
                    new_feature_name=new_col_name,
                    source_cols=[col],
                    formula=f"shift({lag})"
                )
                self.log_info(f"Generated {new_col_name}")
                
        return df_new
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        expected_features = len(self.target_columns) * len(self.lags)
        actual_new_features = len(df_after.columns) - len(df_before.columns)
        
        if actual_new_features != expected_features:
            self.log_warning(f"Verification failed: Expected {expected_features} new features, got {actual_new_features}.")
            return False
        return True
