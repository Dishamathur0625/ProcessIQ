import pandas as pd
from typing import List
from backend.engine.features.base_feature_generator import BaseFeatureGenerator

class OneHotEncoderGenerator(BaseFeatureGenerator):
    """
    Generates One-Hot Encoded features for categorical columns.
    """
    def __init__(self, target_columns: List[str], max_categories: int = 20):
        super().__init__(target_columns)
        self.max_categories = max_categories
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty or not self.target_columns:
            return False
        for col in self.target_columns:
            if col not in df.columns:
                self.log_warning(f"Target column {col} not found in dataset.")
                return False
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        expected_features = 0
        for col in self.target_columns:
            if col in df.columns:
                unique_cats = df[col].nunique()
                expected_features += min(unique_cats, self.max_categories)
        self.log_info(f"Will generate approximately {expected_features} OHE features.")
        return {"expected_features": expected_features}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        df_new = df.copy()
        
        for col in self.target_columns:
            # Handle high cardinality
            top_categories = df_new[col].value_counts().nlargest(self.max_categories).index
            temp_col = df_new[col].where(df_new[col].isin(top_categories), 'Other')
            
            dummies = pd.get_dummies(temp_col, prefix=col, dummy_na=False)
            
            for dummy_col in dummies.columns:
                df_new[dummy_col] = dummies[dummy_col]
                self._create_metadata(
                    new_feature_name=dummy_col,
                    source_cols=[col],
                    formula=f"OHE({col} == {dummy_col.replace(col+'_', '')})"
                )
                self.log_info(f"Generated {dummy_col}")
                
            # Drop original or keep it? Typically feature generators add, but OHE is weird. 
            # We'll just add the features and let Feature Selection decide if original should be dropped.
                
        return df_new
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        if len(df_after.columns) <= len(df_before.columns):
            self.log_warning("Verification failed: No new features generated.")
            return False
        return True
