import pytest
import pandas as pd
import numpy as np
from backend.engine.core.pipeline_executor import PipelineExecutor
from backend.engine.cleaning.imputation.mean_imputation import MeanImputation
from backend.engine.features.general.polynomial_generator import PolynomialFeatureGenerator

def test_empty_dataframe():
    df = pd.DataFrame()
    with pytest.raises(ValueError, match="Dataset validation failed"):
        PipelineExecutor(df)

def test_all_nulls():
    df = pd.DataFrame({
        "A": [np.nan, np.nan, np.nan],
        "B": [np.nan, np.nan, np.nan]
    })
    executor = PipelineExecutor(df)
    
    with pytest.raises(RuntimeError):
        executor.execute_chain([
            MeanImputation(target_columns=["A"])
        ])

def test_wrong_datatypes():
    df = pd.DataFrame({
        "A": ["string1", "string2", "string3"]
    })
    executor = PipelineExecutor(df)
    
    with pytest.raises(ValueError):
        executor.execute_chain([
            PolynomialFeatureGenerator(target_columns=["A"], degrees=[2])
        ])
