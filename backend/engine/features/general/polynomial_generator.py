import pandas as pd
from typing import List
from backend.engine.features.base_feature_generator import BaseFeatureGenerator

class PolynomialFeatureGenerator(BaseFeatureGenerator):
    """
    Generates polynomial features (e.g., Col^2, Col^3) for numeric columns.
    """
    def __init__(self, target_columns: List[str], degrees: List[int] = [2]):
        super().__init__(target_columns)
        self.degrees = degrees
        
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
        expected_features = len(self.target_columns) * len(self.degrees)
        self.log_info(f"Will generate {expected_features} polynomial features.")
        return {"expected_features": expected_features, "degrees": self.degrees}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        df_new = df.copy()
        
        for col in self.target_columns:
            for degree in self.degrees:
                new_col_name = f"{col}_poly_{degree}"
                df_new[new_col_name] = df_new[col] ** degree
                
                self._create_metadata(
                    new_feature_name=new_col_name,
                    source_cols=[col],
                    formula=f"{col}^{degree}"
                )
                self.log_info(f"Generated {new_col_name}")
                
        return df_new
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        expected_features = len(self.target_columns) * len(self.degrees)
        actual_new_features = len(df_after.columns) - len(df_before.columns)
        
        if actual_new_features != expected_features:
            self.log_warning(f"Verification failed: Expected {expected_features} new features, got {actual_new_features}.")
            return False
        return True
