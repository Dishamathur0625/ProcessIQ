import pandas as pd
from typing import List
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from backend.engine.selection.base_feature_selector import BaseFeatureSelector
from backend.engine.core.metadata import FeatureMetadata

class RFESelector(BaseFeatureSelector):
    """
    Recursive Feature Elimination (RFE) to recursively remove the weakest features.
    """
    def __init__(self, metadata_list: List[FeatureMetadata], target_variable: str, is_classification: bool = False, n_features_to_select: int = 10):
        super().__init__(target_variable)
        self.metadata_list = metadata_list
        self.is_classification = is_classification
        self.n_features_to_select = n_features_to_select
        self.selected_features = []
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty or not self.metadata_list:
            return False
        if not self.target_variable or self.target_variable not in df.columns:
            self.log_warning(f"Target variable '{self.target_variable}' is missing.")
            return False
        for meta in self.metadata_list:
            if meta.feature_name not in df.columns:
                self.log_warning(f"Feature {meta.feature_name} not found in dataframe.")
                return False
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        self.log_info(f"Evaluating RFE for {len(self.metadata_list)} features to select {self.n_features_to_select}.")
        return {"features_to_evaluate": len(self.metadata_list), "n_features_to_select": self.n_features_to_select}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        df_clean = df.dropna(subset=[self.target_variable])
        y = df_clean[self.target_variable]
        
        feature_cols = [meta.feature_name for meta in self.metadata_list if meta.feature_name in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean[meta.feature_name])]
        
        if not feature_cols:
            self.log_warning("No numeric features to evaluate.")
            return df
            
        X = df_clean[feature_cols].fillna(df_clean[feature_cols].median())
        
        try:
            if self.is_classification:
                estimator = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
            else:
                estimator = RandomForestRegressor(n_estimators=50, random_state=42, n_jobs=-1)
                
            n_select = min(self.n_features_to_select, len(feature_cols))
            selector = RFE(estimator, n_features_to_select=n_select, step=0.1) # drop 10% each step for speed
            selector.fit(X, y)
            
            # Use inverse ranking as score (rank 1 = best)
            ranks = selector.ranking_
            max_rank = ranks.max() if len(ranks) > 0 else 1
            feature_scores = {feat: float(max_rank - rank + 1) for feat, rank in zip(feature_cols, ranks)}
            
            mask = selector.get_support()
            self.selected_features = [feat for feat, keep in zip(feature_cols, mask) if keep]
            
            reasons = {}
            for feat, keep, rank in zip(feature_cols, mask, ranks):
                if keep:
                    reasons[feat] = f"Selected by RFE (Rank = {rank})"
                else:
                    reasons[feat] = f"Rejected by RFE (Rank = {rank})"
                    
            self._update_metadata(
                metadata_list=self.metadata_list,
                selected_features=self.selected_features,
                scores=feature_scores,
                reasons=reasons,
                selector_name="RFE"
            )
            
            dropped = len(feature_cols) - len(self.selected_features)
            self.log_info(f"Dropped {dropped} features based on RFE. Kept {len(self.selected_features)}.")
            
            cols_to_drop = [f for f in feature_cols if f not in self.selected_features]
            df_new = df.drop(columns=cols_to_drop)
            return df_new
            
        except Exception as e:
            self.log_error(f"RFE selection failed: {str(e)}")
            return df
            
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        return True
