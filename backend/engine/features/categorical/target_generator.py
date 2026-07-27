import pandas as pd
from typing import List
from backend.engine.features.base_feature_generator import BaseFeatureGenerator

class TargetEncoderGenerator(BaseFeatureGenerator):
    """
    Generates Target Encoded features (mapping category to the mean of the target variable).
    """
    def __init__(self, target_columns: List[str], target_variable: str):
        super().__init__(target_columns)
        self.target_variable = target_variable
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty or not self.target_columns:
            return False
        if self.target_variable not in df.columns:
            self.log_warning(f"Target variable {self.target_variable} not found in dataset.")
            return False
        for col in self.target_columns:
            if col not in df.columns:
                self.log_warning(f"Target column {col} not found in dataset.")
                return False
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        expected_features = len(self.target_columns)
        self.log_info(f"Will generate {expected_features} Target Encoded features.")
        return {"expected_features": expected_features, "target_variable": self.target_variable}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        df_new = df.copy()
        
        for col in self.target_columns:
            # Calculate the mean of the target variable grouped by the categorical column
            target_mean_map = df_new.groupby(col)[self.target_variable].mean()
            new_col_name = f"{col}_target_encoded"
            
            # Use global mean for missing categories during mapping
            global_mean = df_new[self.target_variable].mean()
            df_new[new_col_name] = df_new[col].map(target_mean_map).fillna(global_mean)
            
            self._create_metadata(
                new_feature_name=new_col_name,
                source_cols=[col],
                formula=f"TargetEncoder({col}, target={self.target_variable})"
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
