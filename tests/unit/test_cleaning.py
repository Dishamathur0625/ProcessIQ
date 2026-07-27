import pytest
import pandas as pd
import numpy as np
from backend.engine.cleaning.imputation.mean_imputation import MeanImputation
from backend.engine.cleaning.outliers.zscore_removal import ZScoreRemoval

def test_mean_imputation():
    df = pd.DataFrame({
        'A': [1, 2, np.nan, 4, 5],
        'B': [10, 20, 30, np.nan, 50]
    })
    
    op = MeanImputation(target_columns=['A', 'B'])
    result = op.run(df)
    
    # Assert no nulls remain
    assert result.dataset.isna().sum().sum() == 0
    # Assert specific mean values
    assert result.dataset.loc[2, 'A'] == pytest.approx(3.0)
    assert result.dataset.loc[3, 'B'] == pytest.approx(27.5)

def test_zscore_removal():
    # Create an outlier
    df = pd.DataFrame({
        'A': [1, 2, 3, 4, 100000],
        'B': [1, 1, 1, 1, 1]
    })
    
    op = ZScoreRemoval(target_columns=['A'], threshold=1.5)
    result = op.run(df)
    
    # Outlier row should be removed
    assert len(result.dataset) == 4
    assert 100000 not in result.dataset['A'].values
