import pandas as pd
from typing import List
from sklearn.preprocessing import LabelEncoder
from backend.engine.features.base_feature_generator import BaseFeatureGenerator

class LabelEncoderGenerator(BaseFeatureGenerator):
    """
    Generates Label Encoded features (integer mapping) for categorical columns.
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
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        expected_features = len(self.target_columns)
        self.log_info(f"Will generate {expected_features} Label Encoded features.")
        return {"expected_features": expected_features}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        df_new = df.copy()
        
        for col in self.target_columns:
            le = LabelEncoder()
            new_col_name = f"{col}_label_encoded"
            
            # Handle NaNs before encoding
            temp_col = df_new[col].astype(str).fillna("Missing")
            df_new[new_col_name] = le.fit_transform(temp_col)
            
            self._create_metadata(
                new_feature_name=new_col_name,
                source_cols=[col],
                formula=f"LabelEncoder({col})"
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
