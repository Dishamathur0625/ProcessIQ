import pandas as pd
from typing import List, Dict, Any
from datetime import datetime
from backend.engine.core.base_operation import BaseOperation
from backend.engine.core.metadata import FeatureMetadata

class BaseFeatureGenerator(BaseOperation):
    """
    Extends BaseOperation specifically for Feature Engineering.
    Automatically captures FeatureMetadata for lineage tracking.
    """
    def __init__(self, target_columns: List[str]):
        super().__init__()
        self.target_columns = target_columns
        self.generated_features: List[FeatureMetadata] = []
        
    def _create_metadata(self, new_feature_name: str, source_cols: List[str], formula: str) -> FeatureMetadata:
        metadata = FeatureMetadata(
            feature_name=new_feature_name,
            source_columns=source_cols,
            engineering_method=self.operation_name,
            transformation_formula=formula,
            creation_time=datetime.utcnow().isoformat() + "Z"
        )
        self.generated_features.append(metadata)
        return metadata
        
    # Implementations will call self._create_metadata() during execute()
