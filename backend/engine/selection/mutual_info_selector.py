import pandas as pd
from typing import List
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from backend.engine.selection.base_feature_selector import BaseFeatureSelector
from backend.engine.core.metadata import FeatureMetadata

class MutualInformationSelector(BaseFeatureSelector):
    """
    Selects top features based on Mutual Information with the target variable.
    """
    def __init__(self, metadata_list: List[FeatureMetadata], target_variable: str, top_k: int = 10, is_classification: bool = False):
        super().__init__(target_variable)
        self.metadata_list = metadata_list
        self.top_k = top_k
        self.is_classification = is_classification
        self.selected_features = []
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty or not self.metadata_list:
            return False
        if not self.target_variable or self.target_variable not in df.columns:
            self.log_warning(f"Target variable '{self.target_variable}' is missing.")
            return False
        for meta in self.metadata_list:
            if meta.feature_name not in df.columns:
                pass
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        self.log_info(f"Evaluating MI for {len(self.metadata_list)} features. Selecting top {self.top_k}.")
        return {"features_to_evaluate": len(self.metadata_list), "top_k": self.top_k}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        # Drop rows where target is missing for MI calculation
        df_clean = df.dropna(subset=[self.target_variable])
        y = df_clean[self.target_variable]
        
        feature_cols = [meta.feature_name for meta in self.metadata_list if meta.feature_name in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean[meta.feature_name])]
        
        if not feature_cols:
            self.log_warning("No numeric features to evaluate.")
            return df
            
        # Fill NaNs in features for MI calculation
        X = df_clean[feature_cols].fillna(df_clean[feature_cols].median())
        
        if self.is_classification:
            mi_scores = mutual_info_classif(X, y)
        else:
            mi_scores = mutual_info_regression(X, y)
            
        feature_scores = {feat: score for feat, score in zip(feature_cols, mi_scores)}
        
        # Sort and select top_k
        sorted_features = sorted(feature_scores.items(), key=lambda item: item[1], reverse=True)
        self.selected_features = [feat for feat, score in sorted_features[:self.top_k]]
        
        reasons = {}
        for feat, score in sorted_features:
            if feat in self.selected_features:
                reasons[feat] = f"Selected by Mutual Information (Score: {score:.4f}, Rank: <= {self.top_k})"
            else:
                reasons[feat] = f"Rejected by Mutual Information (Score: {score:.4f}, Rank: > {self.top_k})"
                
        self._update_metadata(
            metadata_list=self.metadata_list,
            selected_features=self.selected_features,
            scores=feature_scores,
            reasons=reasons,
            selector_name="MutualInformation"
        )
        
        dropped = len(feature_cols) - len(self.selected_features)
        self.log_info(f"Dropped {dropped} features based on MI. Kept {len(self.selected_features)}.")
        
        cols_to_drop = [f for f in feature_cols if f not in self.selected_features]
        df_new = df.drop(columns=cols_to_drop)
        return df_new
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        return True
