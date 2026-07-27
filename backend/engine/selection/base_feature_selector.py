import pandas as pd
from typing import List, Dict, Optional
from backend.engine.core.base_operation import BaseOperation
from backend.engine.core.metadata import FeatureMetadata

class BaseFeatureSelector(BaseOperation):
    """
    Extends BaseOperation for Feature Selection.
    Consumes FeatureMetadata and marks them as selected/rejected based on scores.
    """
    def __init__(self, target_variable: Optional[str] = None):
        super().__init__()
        self.target_variable = target_variable
        
    def _update_metadata(self, metadata_list: List[FeatureMetadata], selected_features: List[str], scores: Dict[str, float] = None, reasons: Dict[str, str] = None, selector_name: str = None):
        """
        Updates the importance_score, is_selected flags, selection_history, and selection_reason on the metadata objects.
        """
        scores = scores or {}
        reasons = reasons or {}
        selector_name = selector_name or self.__class__.__name__
        
        for meta in metadata_list:
            if meta.feature_name in selected_features:
                meta.is_selected = True
                self.log_info(f"Selected feature: {meta.feature_name}")
            else:
                meta.is_selected = False
                
            if meta.feature_name in scores:
                score = scores[meta.feature_name]
                meta.importance_score = score
                meta.selection_history[selector_name] = score
                
            if meta.feature_name in reasons:
                meta.selection_reason = reasons[meta.feature_name]
                
    def _apply_selection(self, df: pd.DataFrame, selected_features: List[str], keep_originals: bool = True) -> pd.DataFrame:
        """
        Filters the dataframe down to the selected features (and optionally keeps original source columns).
        """
        cols_to_keep = set(selected_features)
        if self.target_variable and self.target_variable in df.columns:
            cols_to_keep.add(self.target_variable)
            
        if keep_originals:
            # We assume non-engineered features (those without metadata or original raw columns) might want to be kept.
            # Real implementation would cross-reference the full dataset schema.
            pass # Skipping complex logic for keeping originals for now to focus on selection logic
            
        return df[list(cols_to_keep.intersection(df.columns))]
