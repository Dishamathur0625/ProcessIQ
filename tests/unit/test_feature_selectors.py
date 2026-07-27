import pytest
import pandas as pd
from backend.engine.selection.variance_selector import VarianceThresholdSelector
from backend.engine.selection.mutual_info_selector import MutualInformationSelector
from backend.engine.core.metadata import FeatureMetadata

def test_variance_selector():
    df = pd.DataFrame({
        'low_var': [1, 1, 1, 1.0001, 1], # variance near 0
        'high_var': [1, 10, 100, 1000, 10000],
        'target': [1, 2, 3, 4, 5]
    })
    
    metadata = [
        FeatureMetadata(feature_name='low_var', source_columns=['a'], transformation_formula='a', engineering_method='mock', creation_time='now'),
        FeatureMetadata(feature_name='high_var', source_columns=['b'], transformation_formula='b', engineering_method='mock', creation_time='now')
    ]
    
    op = VarianceThresholdSelector(metadata_list=metadata, target_variable='target', threshold=0.01)
    op.run(df)
    
    # Check that high_var is selected and low_var is rejected
    assert metadata[1].is_selected == True
    assert metadata[1].selection_history['VarianceThreshold'] > 0
    
    assert metadata[0].selection_history['VarianceThreshold'] == pytest.approx(0.0, abs=1e-8)

def test_mutual_information_selector():
    # target is highly related to good_feat, but not bad_feat
    df = pd.DataFrame({
        'good_feat': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        'bad_feat': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        'target': [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    })
    
    metadata = [
        FeatureMetadata(feature_name='good_feat', source_columns=['a'], transformation_formula='a', engineering_method='mock', creation_time='now'),
        FeatureMetadata(feature_name='bad_feat', source_columns=['b'], transformation_formula='b', engineering_method='mock', creation_time='now')
    ]
    
    op = MutualInformationSelector(metadata_list=metadata, target_variable='target', top_k=1)
    op.run(df)
    
    # good_feat should be selected as top 1
    assert metadata[0].is_selected == True
    assert metadata[1].is_selected == False
