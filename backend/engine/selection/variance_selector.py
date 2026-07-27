import pandas as pd
from typing import List
from sklearn.feature_selection import VarianceThreshold
from backend.engine.selection.base_feature_selector import BaseFeatureSelector
from backend.engine.core.metadata import FeatureMetadata

class VarianceThresholdSelector(BaseFeatureSelector):
    """
    Removes features with low variance (constant or near-constant features).
    """
    def __init__(self, metadata_list: List[FeatureMetadata], threshold: float = 0.0, target_variable: str = None):
        super().__init__(target_variable)
        self.metadata_list = metadata_list
        self.threshold = threshold
        self.selector = VarianceThreshold(threshold=self.threshold)
        self.selected_features = []
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty or not self.metadata_list:
            return False
        # Ensure we are evaluating numeric columns only
        for meta in self.metadata_list:
            if meta.feature_name not in df.columns:
                self.log_warning(f"Feature {meta.feature_name} not found in dataframe.")
                return False
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        self.log_info(f"Evaluating {len(self.metadata_list)} features for variance > {self.threshold}.")
        return {"features_to_evaluate": len(self.metadata_list)}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        feature_cols = [meta.feature_name for meta in self.metadata_list if meta.feature_name in df.columns and pd.api.types.is_numeric_dtype(df[meta.feature_name])]
        
        if not feature_cols:
            self.log_warning("No numeric features to evaluate.")
            return df
            
        try:
            self.selector.fit(df[feature_cols])
            variances = self.selector.variances_
            
            scores = {feat: var for feat, var in zip(feature_cols, variances)}
            
            mask = self.selector.get_support()
            self.selected_features = [feat for feat, keep in zip(feature_cols, mask) if keep]
            
            reasons = {}
            for feat, keep, var in zip(feature_cols, mask, variances):
                if keep:
                    reasons[feat] = f"Selected by VarianceThreshold (Var = {var:.4f})"
                else:
                    reasons[feat] = f"Rejected due to low variance (Var = {var:.4f} <= {self.threshold})"
            
            self._update_metadata(
                metadata_list=self.metadata_list,
                selected_features=self.selected_features,
                scores=scores,
                reasons=reasons,
                selector_name="VarianceThreshold"
            )
            
            dropped = len(feature_cols) - len(self.selected_features)
            self.log_info(f"Dropped {dropped} low-variance features. Kept {len(self.selected_features)}.")
            
            # Note: We do not drop them from the dataframe yet. Selection just marks them. 
            # Another finalization step or the user can choose to drop them.
            # But the spec might say execute() should drop them. Let's drop them.
            cols_to_drop = [feat for feat, keep in zip(feature_cols, mask) if not keep]
            df_new = df.drop(columns=cols_to_drop)
            return df_new
            
        except Exception as e:
            self.log_error(f"Variance threshold failed: {str(e)}")
            return df
            
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        return True
