import pandas as pd
from typing import List
from sklearn.feature_selection import chi2, SelectKBest
from backend.engine.selection.base_feature_selector import BaseFeatureSelector
from backend.engine.core.metadata import FeatureMetadata

class ChiSquareSelector(BaseFeatureSelector):
    """
    Selects top features based on Chi-Square statistic.
    Only applicable for non-negative features (typically categorical/boolean).
    """
    def __init__(self, metadata_list: List[FeatureMetadata], target_variable: str, top_k: int = 10):
        super().__init__(target_variable)
        self.metadata_list = metadata_list
        self.top_k = top_k
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
        self.log_info(f"Evaluating Chi2 for {len(self.metadata_list)} features. Selecting top {self.top_k}.")
        return {"features_to_evaluate": len(self.metadata_list), "top_k": self.top_k}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        df_clean = df.dropna(subset=[self.target_variable])
        y = df_clean[self.target_variable]
        
        # Chi2 requires non-negative features. We'll filter for numeric, non-negative.
        feature_cols = []
        for meta in self.metadata_list:
            col = meta.feature_name
            if pd.api.types.is_numeric_dtype(df_clean[col]):
                if df_clean[col].min() >= 0:
                    feature_cols.append(col)
                    
        if not feature_cols:
            self.log_warning("No non-negative numeric features to evaluate for Chi2.")
            return df
            
        X = df_clean[feature_cols].fillna(df_clean[feature_cols].median())
        
        try:
            k = min(self.top_k, len(feature_cols))
            selector = SelectKBest(score_func=chi2, k=k)
            selector.fit(X, y)
            
            chi2_scores = selector.scores_
            feature_scores = {feat: score for feat, score in zip(feature_cols, chi2_scores)}
            
            mask = selector.get_support()
            self.selected_features = [feat for feat, keep in zip(feature_cols, mask) if keep]
            
            reasons = {}
            for feat, keep, score in zip(feature_cols, mask, chi2_scores):
                if keep:
                    reasons[feat] = f"Selected by Chi-Square (Score: {score:.4f})"
                else:
                    reasons[feat] = f"Rejected by Chi-Square (Score: {score:.4f})"
                    
            self._update_metadata(
                metadata_list=self.metadata_list,
                selected_features=self.selected_features,
                scores=feature_scores,
                reasons=reasons,
                selector_name="ChiSquare"
            )
            
            dropped = len(feature_cols) - len(self.selected_features)
            self.log_info(f"Dropped {dropped} features based on Chi2. Kept {len(self.selected_features)}.")
            
            cols_to_drop = [f for f in feature_cols if f not in self.selected_features]
            df_new = df.drop(columns=cols_to_drop)
            return df_new
            
        except Exception as e:
            self.log_error(f"Chi-Square selection failed: {str(e)}")
            return df
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        return True
