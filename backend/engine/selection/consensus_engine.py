import pandas as pd
from typing import List, Dict, Any
from backend.engine.core.base_operation import BaseOperation
from backend.engine.core.metadata import FeatureMetadata

class FeatureSelectionConsensus(BaseOperation):
    """
    Aggregates scores and decisions from multiple independent Feature Selectors.
    Produces a final ranked list of features with confidence scores.
    """
    def __init__(self, metadata_list: List[FeatureMetadata], target_variable: str, approval_threshold: float = 0.5):
        super().__init__()
        self.metadata_list = metadata_list
        self.target_variable = target_variable
        self.approval_threshold = approval_threshold
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty or not self.metadata_list:
            return False
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        self.log_info(f"Running consensus across {len(self.metadata_list)} evaluated features.")
        return {"features_to_evaluate": len(self.metadata_list)}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        consensus_scores = []
        
        for meta in self.metadata_list:
            history = meta.selection_history
            if not history:
                # If a feature bypassed selection or wasn't evaluated, give it a baseline or drop it.
                # Assuming if it has no history, it wasn't selected by anything.
                total_selectors = 1 # avoid div by zero
                votes = 0
            else:
                total_selectors = len(history)
                votes = 0
                
                # Simple voting mechanism based on scores in history
                for selector, score in history.items():
                    # For Boruta, 2.0 = confirmed, 1.0 = tentative. Treat both as a vote, but maybe weight confirmed more
                    if selector == "Boruta":
                        if score >= 1.0: votes += (score / 2.0) # 1.0 for confirmed, 0.5 for tentative
                    elif selector == "CorrelationFilter":
                        if score == 1.0: votes += 1
                    elif selector == "VarianceThreshold":
                        if score > 0.0: votes += 1
                    elif selector in ["MutualInformation", "ANOVA", "ChiSquare", "RFE", "L1Lasso"]:
                        # For continuous rank/score based selectors, if they recorded a score > 0, it's a weak vote.
                        # Ideally these selectors recorded 1.0 or high ranks, but we simplify for now.
                        # RFE gave inverted ranks. Let's assume if it has a score > 0 it was selected in top_k.
                        # For a robust implementation, selectors should standardize their output into 'votes' or 'normalized_scores'.
                        if score > 0.0: votes += 1
                        
            confidence = (votes / total_selectors) if total_selectors > 0 else 0.0
            consensus_scores.append((meta, confidence))
            
        # Sort by confidence descending
        consensus_scores.sort(key=lambda x: x[1], reverse=True)
        
        selected_columns = []
        if self.target_variable in df.columns:
            selected_columns.append(self.target_variable)
            
        for rank, (meta, confidence) in enumerate(consensus_scores, start=1):
            meta.final_rank = rank
            meta.final_confidence = confidence
            
            if confidence >= self.approval_threshold:
                meta.is_selected = True
                meta.selection_reason = f"Selected by Consensus Engine (Confidence: {confidence:.2f}, Rank: {rank})"
                selected_columns.append(meta.feature_name)
            else:
                meta.is_selected = False
                meta.selection_reason = f"Rejected by Consensus Engine (Confidence: {confidence:.2f} < {self.approval_threshold})"
                
        self.log_info(f"Consensus approved {len(selected_columns) - 1} features (excluding target).")
        
        # Ensure we don't drop original columns that didn't go through feature engineering metadata (if any)
        # For strict pipeline, we only keep what's approved + target.
        cols_to_keep = [col for col in selected_columns if col in df.columns]
        
        return df[cols_to_keep]
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        return True
