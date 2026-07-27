import pandas as pd
from typing import List
from sklearn.feature_selection import f_classif, f_regression, SelectKBest
from backend.engine.selection.base_feature_selector import BaseFeatureSelector
from backend.engine.core.metadata import FeatureMetadata

class ANOVASelector(BaseFeatureSelector):
    """
    Selects top features based on ANOVA F-value between label/feature.
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
                self.log_warning(f"Feature {meta.feature_name} not found in dataframe.")
                return False
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        self.log_info(f"Evaluating ANOVA for {len(self.metadata_list)} features. Selecting top {self.top_k}.")
        return {"features_to_evaluate": len(self.metadata_list), "top_k": self.top_k}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        df_clean = df.dropna(subset=[self.target_variable])
        y = df_clean[self.target_variable]
        
        feature_cols = [meta.feature_name for meta in self.metadata_list if meta.feature_name in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean[meta.feature_name])]
        
        if not feature_cols:
            self.log_warning("No numeric features to evaluate.")
            return df
            
        X = df_clean[feature_cols].fillna(df_clean[feature_cols].median())
        
        try:
            score_func = f_classif if self.is_classification else f_regression
            k = min(self.top_k, len(feature_cols))
            selector = SelectKBest(score_func=score_func, k=k)
            selector.fit(X, y)
            
            f_scores = selector.scores_
            feature_scores = {feat: score for feat, score in zip(feature_cols, f_scores)}
            
            mask = selector.get_support()
            self.selected_features = [feat for feat, keep in zip(feature_cols, mask) if keep]
            
            reasons = {}
            for feat, keep, score in zip(feature_cols, mask, f_scores):
                if keep:
                    reasons[feat] = f"Selected by ANOVA (F-Score: {score:.4f})"
                else:
                    reasons[feat] = f"Rejected by ANOVA (F-Score: {score:.4f})"
                    
            self._update_metadata(
                metadata_list=self.metadata_list,
                selected_features=self.selected_features,
                scores=feature_scores,
                reasons=reasons,
                selector_name="ANOVA"
            )
            
            dropped = len(feature_cols) - len(self.selected_features)
            self.log_info(f"Dropped {dropped} features based on ANOVA. Kept {len(self.selected_features)}.")
            
            cols_to_drop = [f for f in feature_cols if f not in self.selected_features]
            df_new = df.drop(columns=cols_to_drop)
            return df_new
            
        except Exception as e:
            self.log_error(f"ANOVA selection failed: {str(e)}")
            return df
            
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        return True
