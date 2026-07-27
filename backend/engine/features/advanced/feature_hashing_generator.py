import pandas as pd
from typing import List
from sklearn.feature_extraction import FeatureHasher
from backend.engine.features.base_feature_generator import BaseFeatureGenerator

class FeatureHashingGenerator(BaseFeatureGenerator):
    """
    Generates Feature Hashed features for high-cardinality categorical columns.
    """
    def __init__(self, target_columns: List[str], n_features: int = 10):
        super().__init__(target_columns)
        self.n_features = n_features
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty or not self.target_columns:
            return False
        for col in self.target_columns:
            if col not in df.columns:
                self.log_warning(f"Target column {col} not found in dataset.")
                return False
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        expected_features = self.n_features
        self.log_info(f"Will generate {expected_features} Hashed features combining {len(self.target_columns)} columns.")
        return {"expected_features": expected_features, "n_features": self.n_features}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        df_new = df.copy()
        
        # Feature hashing takes dictionaries or strings
        # Convert specified columns to strings
        hash_input = df_new[self.target_columns].astype(str).to_dict(orient='records')
        
        hasher = FeatureHasher(n_features=self.n_features, input_type='dict')
        hashed_features = hasher.transform(hash_input).toarray()
        
        for i in range(self.n_features):
            new_col_name = f"hashed_feature_{i}"
            df_new[new_col_name] = hashed_features[:, i]
            
            self._create_metadata(
                new_feature_name=new_col_name,
                source_cols=self.target_columns,
                formula=f"FeatureHasher({i})"
            )
            self.log_info(f"Generated {new_col_name}")
                
        return df_new
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        expected_features = self.n_features
        actual_new_features = len(df_after.columns) - len(df_before.columns)
        
        if actual_new_features != expected_features:
            self.log_warning(f"Verification failed: Expected {expected_features} new features, got {actual_new_features}.")
            return False
        return True
