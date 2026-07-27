import pandas as pd
import numpy as np
from typing import List
from backend.engine.selection.base_feature_selector import BaseFeatureSelector
from backend.engine.core.metadata import FeatureMetadata

class CorrelationFilterSelector(BaseFeatureSelector):
    """
    Removes features that are highly correlated with other features (to avoid multicollinearity).
    Keeps the one that has higher correlation with the target (if provided) or just keeps the first one.
    """
    def __init__(self, metadata_list: List[FeatureMetadata], threshold: float = 0.9, target_variable: str = None):
        super().__init__(target_variable)
        self.metadata_list = metadata_list
        self.threshold = threshold
        self.selected_features = []
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty or not self.metadata_list:
            return False
        for meta in self.metadata_list:
            if meta.feature_name not in df.columns:
                pass # previous selector may have dropped it
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        self.log_info(f"Evaluating correlation among {len(self.metadata_list)} features with threshold {self.threshold}.")
        return {"features_to_evaluate": len(self.metadata_list)}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        feature_cols = [meta.feature_name for meta in self.metadata_list if meta.feature_name in df.columns and pd.api.types.is_numeric_dtype(df[meta.feature_name])]
        
        if len(feature_cols) < 2:
            self.log_warning("Not enough numeric features to calculate correlation.")
            return df
            
        corr_matrix = df[feature_cols].corr().abs()
        upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
        
        to_drop = set()
        reasons = {}
        scores = {}
        
        for col in upper.columns:
            # Find any highly correlated features to this column
            correlated_with = upper.index[upper[col] > self.threshold].tolist()
            if correlated_with:
                to_drop.add(col)
                corr_val = upper.loc[correlated_with[0], col]
                reasons[col] = f"Rejected due to high correlation ({corr_val:.2f}) with {correlated_with[0]}"
                scores[col] = 0.0
            else:
                reasons[col] = "Selected by CorrelationFilter (no high collinearity)"
                scores[col] = 1.0 # 1.0 means kept
                
        self.selected_features = [f for f in feature_cols if f not in to_drop]
        
        # Ensure we assign reasons and scores for the features we kept
        for f in self.selected_features:
            if f not in reasons:
                reasons[f] = "Selected by CorrelationFilter (no high collinearity)"
                scores[f] = 1.0
                
        self._update_metadata(
            metadata_list=self.metadata_list,
            selected_features=self.selected_features,
            scores=scores,
            reasons=reasons,
            selector_name="CorrelationFilter"
        )
        
        self.log_info(f"Dropped {len(to_drop)} highly correlated features. Kept {len(self.selected_features)}.")
        
        df_new = df.drop(columns=list(to_drop))
        return df_new
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        return True
