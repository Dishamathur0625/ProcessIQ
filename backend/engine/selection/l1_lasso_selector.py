import pandas as pd
import numpy as np
from typing import List
from sklearn.linear_model import Lasso, LogisticRegression
from sklearn.feature_selection import SelectFromModel
from backend.engine.selection.base_feature_selector import BaseFeatureSelector
from backend.engine.core.metadata import FeatureMetadata

class L1LassoSelector(BaseFeatureSelector):
    """
    Selects features using L1 regularization (LASSO) which shrinks less important feature coefficients to 0.
    """
    def __init__(self, metadata_list: List[FeatureMetadata], target_variable: str, is_classification: bool = False, alpha: float = 0.01):
        super().__init__(target_variable)
        self.metadata_list = metadata_list
        self.is_classification = is_classification
        self.alpha = alpha
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
        self.log_info(f"Evaluating L1 LASSO for {len(self.metadata_list)} features.")
        return {"features_to_evaluate": len(self.metadata_list), "alpha": self.alpha}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        df_clean = df.dropna(subset=[self.target_variable])
        y = df_clean[self.target_variable]
        
        feature_cols = [meta.feature_name for meta in self.metadata_list if meta.feature_name in df_clean.columns and pd.api.types.is_numeric_dtype(df_clean[meta.feature_name])]
        
        if not feature_cols:
            self.log_warning("No numeric features to evaluate.")
            return df
            
        # L1 requires scaled data typically, but for generic selection we just fill NaNs
        X = df_clean[feature_cols].fillna(df_clean[feature_cols].median())
        
        try:
            if self.is_classification:
                # LogisticRegression with L1 penalty
                estimator = LogisticRegression(penalty='l1', solver='liblinear', C=1/self.alpha, random_state=42)
            else:
                # Lasso Regressor
                estimator = Lasso(alpha=self.alpha, random_state=42)
                
            selector = SelectFromModel(estimator)
            selector.fit(X, y)
            
            # Get coefficients (could be 1D or 2D for multiclass)
            if hasattr(selector.estimator_, 'coef_'):
                coefs = np.abs(selector.estimator_.coef_)
                if coefs.ndim > 1:
                    coefs = np.mean(coefs, axis=0) # Average across classes if multiclass
            else:
                coefs = np.zeros(len(feature_cols))
                
            feature_scores = {feat: float(coef) for feat, coef in zip(feature_cols, coefs)}
            
            mask = selector.get_support()
            self.selected_features = [feat for feat, keep in zip(feature_cols, mask) if keep]
            
            reasons = {}
            for feat, keep, coef in zip(feature_cols, mask, coefs):
                if keep:
                    reasons[feat] = f"Selected by LASSO (Coefficient = {coef:.4f})"
                else:
                    reasons[feat] = f"Rejected by LASSO (Coefficient shrunk to {coef:.4f})"
                    
            self._update_metadata(
                metadata_list=self.metadata_list,
                selected_features=self.selected_features,
                scores=feature_scores,
                reasons=reasons,
                selector_name="L1Lasso"
            )
            
            dropped = len(feature_cols) - len(self.selected_features)
            self.log_info(f"Dropped {dropped} features based on L1 LASSO. Kept {len(self.selected_features)}.")
            
            cols_to_drop = [f for f in feature_cols if f not in self.selected_features]
            df_new = df.drop(columns=cols_to_drop)
            return df_new
            
        except Exception as e:
            self.log_error(f"L1 LASSO selection failed: {str(e)}")
            return df
            
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        return True
