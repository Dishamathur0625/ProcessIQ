import pandas as pd
from typing import List
from backend.engine.features.base_feature_generator import BaseFeatureGenerator

class PercentageChangeGenerator(BaseFeatureGenerator):
    """
    Generates percentage change features (e.g., current/previous - 1).
    """
    def __init__(self, target_columns: List[str], periods: List[int] = [1]):
        super().__init__(target_columns)
        self.periods = periods
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty or not self.target_columns:
            return False
        for col in self.target_columns:
            if col not in df.columns:
                self.log_warning(f"Target column {col} not found in dataset.")
                return False
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        expected_features = len(self.target_columns) * len(self.periods)
        self.log_info(f"Will generate {expected_features} pct change features.")
        return {"expected_features": expected_features, "periods": self.periods}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        df_new = df.copy()
        
        for col in self.target_columns:
            for period in self.periods:
                new_col_name = f"{col}_pct_change_{period}"
                df_new[new_col_name] = df_new[col].pct_change(periods=period)
                
                self._create_metadata(
                    new_feature_name=new_col_name,
                    source_cols=[col],
                    formula=f"pct_change({period})"
                )
                self.log_info(f"Generated {new_col_name}")
                
        return df_new
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        expected_features = len(self.target_columns) * len(self.periods)
        actual_new_features = len(df_after.columns) - len(df_before.columns)
        
        if actual_new_features != expected_features:
            self.log_warning(f"Verification failed: Expected {expected_features} new features, got {actual_new_features}.")
            return False
        return True
