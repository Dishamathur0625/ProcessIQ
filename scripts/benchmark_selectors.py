import pandas as pd
import numpy as np
from backend.engine.core.metadata import FeatureMetadata
from backend.engine.selection.variance_selector import VarianceThresholdSelector
from backend.engine.selection.correlation_selector import CorrelationFilterSelector
from backend.engine.selection.mutual_info_selector import MutualInformationSelector
from backend.engine.selection.consensus_engine import FeatureSelectionConsensus

def test_feature_selection():
    # 1. Create a dummy dataset
    np.random.seed(42)
    df = pd.DataFrame({
        "target": np.random.randn(100),
        "feat_1_good": np.random.randn(100),
        "feat_2_good": np.random.randn(100),
        "feat_3_noise": np.random.randn(100),
        "feat_4_constant": np.ones(100), # should be removed by variance
    })
    
    # Make feat_1 highly correlated with target
    df["feat_1_good"] = df["target"] * 0.9 + np.random.randn(100) * 0.1
    # Make feat_5 highly correlated with feat_2
    df["feat_5_corr"] = df["feat_2_good"] * 0.99 + np.random.randn(100) * 0.01
    
    # 2. Create mock FeatureMetadata
    features = ["feat_1_good", "feat_2_good", "feat_3_noise", "feat_4_constant", "feat_5_corr"]
    metadata_list = []
    for f in features:
        metadata_list.append(FeatureMetadata(
            feature_name=f,
            source_columns=["raw_col"],
            engineering_method="MockGenerator",
            transformation_formula="mock",
            creation_time="now"
        ))
        
    print(f"Original dataset shape: {df.shape}")
    
    # 3. Run Selectors sequentially (simulating independent or sequential runs)
    
    # Variance
    var_sel = VarianceThresholdSelector(metadata_list, threshold=0.0, target_variable="target")
    df = var_sel.run(df).dataset
    print(f"After Variance Selector: {df.columns.tolist()}")
    
    # Correlation
    corr_sel = CorrelationFilterSelector(metadata_list, threshold=0.9, target_variable="target")
    df = corr_sel.run(df).dataset
    print(f"After Correlation Selector: {df.columns.tolist()}")
    
    # Mutual Info
    mi_sel = MutualInformationSelector(metadata_list, target_variable="target", top_k=2)
    df = mi_sel.run(df).dataset
    print(f"After MI Selector: {df.columns.tolist()}")
    
    # 4. Consensus Engine
    print("\n--- Running Consensus Engine ---")
    consensus = FeatureSelectionConsensus(metadata_list, target_variable="target", approval_threshold=0.5)
    df_final = consensus.run(df).dataset
    
    print(f"\nFinal Selected Features: {df_final.columns.tolist()}")
    
    print("\nMetadata Audit:")
    for meta in metadata_list:
        print(f"Feature: {meta.feature_name} | Selected: {meta.is_selected} | Reason: {meta.selection_reason} | History: {meta.selection_history}")

if __name__ == "__main__":
    test_feature_selection()
