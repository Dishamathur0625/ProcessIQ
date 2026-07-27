import pandas as pd
import numpy as np
from typing import List
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from backend.engine.selection.base_feature_selector import BaseFeatureSelector
from backend.engine.core.metadata import FeatureMetadata

# Optional import, fallback if boruta is not installed
try:
    from boruta import BorutaPy
    HAS_BORUTA = True
except ImportError:
    HAS_BORUTA = False

class BorutaSelector(BaseFeatureSelector):
    """
    Boruta Feature Selection (Wrapper around random forest that compares features against shadow features).
    """
    def __init__(self, metadata_list: List[FeatureMetadata], target_variable: str, is_classification: bool = False):
        super().__init__(target_variable)
        self.metadata_list = metadata_list
        self.is_classification = is_classification
        self.selected_features = []
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty or not self.metadata_list:
            return False
        if not self.target_variable or self.target_variable not in df.columns:
            self.log_warning(f"Target variable '{self.target_variable}' is missing.")
            return False
        if not HAS_BORUTA:
            self.log_warning("BorutaPy is not installed. Skipping Boruta selection.")
            return False
        for meta in self.metadata_list:
            if meta.feature_name not in df.columns:
                self.log_warning(f"Feature {meta.feature_name} not found in dataframe.")
                return False
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        self.log_info(f"Evaluating Boruta for {len(self.metadata_list)} features.")
        return {"features_to_evaluate": len(self.metadata_list)}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        df_clean = df.dropna(subset=[self.target_variable])
        y = df_clean[self.target_variable].values
        
        feature_cols = [meta.feature_name for meta in self.metadata_list if meta.feature_name in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean[meta.feature_name])]
        
        if not feature_cols:
            self.log_warning("No numeric features to evaluate.")
            return df
            
        X = df_clean[feature_cols].fillna(df_clean[feature_cols].median()).values
        
        try:
            if self.is_classification:
                estimator = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42, n_jobs=-1)
            else:
                estimator = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42, n_jobs=-1)
                
            selector = BorutaPy(estimator, n_estimators='auto', verbose=0, random_state=42)
            selector.fit(X, y)
            
            mask = selector.support_ # Confirmed features
            tentative_mask = selector.support_weak_ # Tentative features
            
            self.selected_features = [feat for feat, keep in zip(feature_cols, mask) if keep]
            
            # For Boruta, score can be 2 (Confirmed), 1 (Tentative), 0 (Rejected)
            feature_scores = {}
            reasons = {}
            
            for feat, is_confirmed, is_tentative in zip(feature_cols, mask, tentative_mask):
                if is_confirmed:
                    feature_scores[feat] = 2.0
                    reasons[feat] = "Selected by Boruta (Confirmed)"
                elif is_tentative:
                    feature_scores[feat] = 1.0
                    reasons[feat] = "Rejected by Boruta (Tentative - Did not pass strict threshold)"
                else:
                    feature_scores[feat] = 0.0
                    reasons[feat] = "Rejected by Boruta (Failed against shadow features)"
                    
            self._update_metadata(
                metadata_list=self.metadata_list,
                selected_features=self.selected_features,
                scores=feature_scores,
                reasons=reasons,
                selector_name="Boruta"
            )
            
            dropped = len(feature_cols) - len(self.selected_features)
            self.log_info(f"Dropped {dropped} features based on Boruta. Kept {len(self.selected_features)}.")
            
            cols_to_drop = [f for f in feature_cols if f not in self.selected_features]
            df_new = df.drop(columns=cols_to_drop)
            return df_new
            
        except Exception as e:
            self.log_error(f"Boruta selection failed: {str(e)}")
            return df
            
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        return True
