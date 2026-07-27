import pandas as pd
import numpy as np
from backend.engine.core.pipeline_executor import PipelineExecutor
from backend.engine.features.timeseries.lag_generator import LagFeatureGenerator
from backend.engine.features.general.polynomial_generator import PolynomialFeatureGenerator
from backend.engine.selection.variance_selector import VarianceThresholdSelector
from backend.engine.selection.mutual_info_selector import MutualInformationSelector
from backend.engine.selection.consensus_engine import FeatureSelectionConsensus
from backend.engine.cleaning.imputation.mean_imputation import MeanImputation
from backend.engine.validation.missing_value_validator import MissingValueValidator

def run_end_to_end():
    print("=== ProcessIQ End-to-End Pipeline Demo ===")
    
    # 1. Simulate Raw Upload Dataset
    np.random.seed(42)
    df = pd.DataFrame({
        "temperature": np.random.randn(100) * 10 + 20,
        "pressure": np.random.randn(100) * 5 + 100,
        "vibration_noise": np.random.randn(100),
        "constant_sensor": np.ones(100),
        "target_yield": np.random.randn(100) # What we want to predict
    })
    
    # Introduce some missing values to test cleaning
    df.loc[10:15, "temperature"] = np.nan
    
    # Correlate vibration to target to ensure it gets selected
    df["vibration_noise"] = df["target_yield"] * 0.8 + np.random.randn(100) * 0.2
    
    print(f"\n1. Raw Dataset Loaded. Shape: {df.shape}")
    print(f"Missing Values:\n{df.isnull().sum()}")
    
    # 2. Initialize Pipeline Executor (Automatically profiles initial state)
    executor = PipelineExecutor(df, user_id="system_demo")
    print(f"\n2. Initial Profile Completed. Fingerprint: {executor.version_graph.current_version_id}")
    
    # 3. Validation & Cleaning
    print("\n3. Running Validation & Cleaning...")
    cleaning_ops = [
        MeanImputation(target_columns=["temperature"])
    ]
    executor.execute_chain(cleaning_ops)
    
    # 4. Feature Engineering
    print("\n4. Running Feature Engineering...")
    engineering_ops = [
        LagFeatureGenerator(target_columns=["temperature", "pressure"], lags=[1]),
        PolynomialFeatureGenerator(target_columns=["temperature"], degrees=[2])
    ]
    executor.execute_chain(engineering_ops)
    
    # We now have generated metadata in the executor!
    generated_metadata = executor.feature_metadata_registry
    print(f"Generated {len(generated_metadata)} new features with full cryptographic lineage.")
    
    # 5. Feature Selection
    print("\n5. Running Feature Selection Gauntlet...")
    # Note: Target is 'target_yield'
    selection_ops = [
        VarianceThresholdSelector(metadata_list=generated_metadata, threshold=0.01, target_variable="target_yield"),
        MutualInformationSelector(metadata_list=generated_metadata, target_variable="target_yield", top_k=2),
        FeatureSelectionConsensus(metadata_list=generated_metadata, target_variable="target_yield", approval_threshold=0.5)
    ]
    
    result = executor.execute_chain(selection_ops)
    
    # 6. Final Outputs
    final_df = result["final_dataset"]
    print(f"\n6. Pipeline Complete! Final Dataset Shape: {final_df.shape}")
    print(f"Final Columns: {final_df.columns.tolist()}")
    
    print("\n--- Explainability Report Snippet ---")
    for meta in result["feature_metadata"]:
        status = "✅ ACCEPTED" if meta.is_selected else "❌ REJECTED"
        print(f"{status} | {meta.feature_name} | {meta.selection_reason}")
        
    print("\n--- Audit Trail Snippet ---")
    for audit in result["audit_trail"][-2:]: # Show last two steps
        print(f"Step: {audit['operation_name']} -> Version Hash: {audit['dataset_version_id']}")

if __name__ == "__main__":
    run_end_to_end()
