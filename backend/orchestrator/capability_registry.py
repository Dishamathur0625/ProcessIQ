from typing import Dict, List
from pydantic import BaseModel

class Capability(BaseModel):
    inputs: List[str]
    requires: List[str]
    outputs: List[str]
    description: str

CAPABILITY_REGISTRY: Dict[str, Capability] = {
    "median_imputation": Capability(
        inputs=["numeric"],
        requires=["missing_values"],
        outputs=["cleaned_dataset"],
        description="Replaces missing numeric values with the median of the column."
    ),
    "drop_duplicates": Capability(
        inputs=["all"],
        requires=["duplicates"],
        outputs=["cleaned_dataset"],
        description="Removes identical rows."
    ),
    "isolation_forest_outliers": Capability(
        inputs=["numeric"],
        requires=[],
        outputs=["outlier_flags"],
        description="Detects anomalies using Isolation Forest."
    ),
    "standard_scaler": Capability(
        inputs=["numeric"],
        requires=[],
        outputs=["scaled_features"],
        description="Standardizes features by removing the mean and scaling to unit variance."
    )
}
