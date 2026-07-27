import pytest
import pandas as pd
from backend.engine.features.general.polynomial_generator import PolynomialFeatureGenerator
from backend.engine.features.timeseries.lag_generator import LagFeatureGenerator
from backend.engine.features.categorical.one_hot_generator import OneHotEncoderGenerator

def test_polynomial_generator():
    df = pd.DataFrame({
        'A': [1, 2, 3],
        'B': [4, 5, 6]
    })
    
    op = PolynomialFeatureGenerator(target_columns=['A', 'B'], degrees=[2])
    result = op.run(df)
    
    # Check if A^2 and B^2 were generated
    assert 'A_poly_2' in result.dataset.columns
    assert 'B_poly_2' in result.dataset.columns
    assert result.dataset.loc[1, 'A_poly_2'] == 4.0
    
    # Metadata check
    assert len(result.feature_metadata) == 2
    assert result.feature_metadata[0].feature_name == 'A_poly_2'
    assert result.feature_metadata[0].source_columns == ['A']

def test_lag_generator():
    df = pd.DataFrame({
        'sensor': [10, 20, 30, 40]
    })
    
    op = LagFeatureGenerator(target_columns=['sensor'], lags=[1, 2])
    result = op.run(df)
    
    assert 'sensor_lag_1' in result.dataset.columns
    assert 'sensor_lag_2' in result.dataset.columns
    
    # Check shifted values
    assert pd.isna(result.dataset.loc[0, 'sensor_lag_1'])
    assert result.dataset.loc[1, 'sensor_lag_1'] == 10.0
    assert result.dataset.loc[2, 'sensor_lag_2'] == 10.0

def test_one_hot_generator():
    df = pd.DataFrame({
        'color': ['red', 'blue', 'red']
    })
    
    op = OneHotEncoderGenerator(target_columns=['color'])
    result = op.run(df)
    
    # red and blue columns
    assert 'color_red' in result.dataset.columns
    assert 'color_blue' in result.dataset.columns
    
    assert result.dataset.loc[0, 'color_red'] == 1
    assert result.dataset.loc[0, 'color_blue'] == 0
