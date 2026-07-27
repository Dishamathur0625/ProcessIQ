import pandas as pd
import itertools
from typing import List
from backend.engine.features.base_feature_generator import BaseFeatureGenerator

class RatioFeatureGenerator(BaseFeatureGenerator):
    """
    Generates ratio features (e.g., Col1 / Col2) between numeric columns.
    Handles division by zero by replacing with NaN or 0.
    """
    def __init__(self, target_columns: List[str]):
        super().__init__(target_columns)
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty or len(self.target_columns) < 2:
            self.log_warning("Requires at least two target columns.")
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
        # Permutations, since Col1 / Col2 != Col2 / Col1
        expected_features = len(list(itertools.permutations(self.target_columns, 2)))
        self.log_info(f"Will generate {expected_features} ratio features.")
        return {"expected_features": expected_features}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        df_new = df.copy()
        
        pairs = list(itertools.permutations(self.target_columns, 2))
        for col1, col2 in pairs:
            new_col_name = f"{col1}_over_{col2}"
            
            # Avoid division by zero warning, map zero div to NaN
            df_new[new_col_name] = df_new[col1] / df_new[col2].replace(0, pd.NA)
            
            self._create_metadata(
                new_feature_name=new_col_name,
                source_cols=[col1, col2],
                formula=f"{col1} / {col2}"
            )
            self.log_info(f"Generated {new_col_name}")
                
        return df_new
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        expected_features = len(list(itertools.permutations(self.target_columns, 2)))
        actual_new_features = len(df_after.columns) - len(df_before.columns)
        
        if actual_new_features != expected_features:
            self.log_warning(f"Verification failed: Expected {expected_features} new features, got {actual_new_features}.")
            return False
        return True
