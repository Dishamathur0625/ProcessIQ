import pandas as pd
import numpy as np
import time
from backend.engine.core.pipeline_executor import PipelineExecutor
from backend.engine.features.timeseries.lag_generator import LagFeatureGenerator
from backend.engine.features.general.polynomial_generator import PolynomialFeatureGenerator
from backend.engine.selection.variance_selector import VarianceThresholdSelector
from backend.engine.selection.mutual_info_selector import MutualInformationSelector
from backend.engine.selection.consensus_engine import FeatureSelectionConsensus
from backend.engine.cleaning.imputation.mean_imputation import MeanImputation
from backend.engine.visualization.spec_generator import VisualizationSpecificationGenerator
from backend.engine.reports.analytics_summary_report import AnalyticsSummaryReportGenerator
from backend.engine.reports.manifest_generator import AnalyticsEngineManifestGenerator
from backend.engine.reports.auto_doc_generator import AutoDocGenerator

def generate_mock_data(rows=1000):
    np.random.seed(42)
    df = pd.DataFrame({
        "temperature": np.random.randn(rows) * 10 + 20,
        "pressure": np.random.randn(rows) * 5 + 100,
        "vibration_noise": np.random.randn(rows),
        "constant_sensor": np.ones(rows),
        "target_yield": np.random.randn(rows)
    })
    # Inject missing values
    df.loc[:int(rows*0.1), "temperature"] = np.nan
    # Inject correlation
    df["vibration_noise"] = df["target_yield"] * 0.8 + np.random.randn(rows) * 0.2
    return df

def run_benchmark():
    print("=========================================================")
    print("        ProcessIQ Analytics Engine v1.0 Benchmark        ")
    print("=========================================================")
    
    df = generate_mock_data(5000)
    print(f"Dataset Shape: {df.shape}")
    
    start_time = time.time()
    
    # 1. Initialize Pipeline
    executor = PipelineExecutor(df, user_id="benchmark_user")
    
    # 2. Define Operations
    ops = [
        MeanImputation(target_columns=["temperature"]),
        LagFeatureGenerator(target_columns=["temperature", "pressure"], lags=[1, 2]),
        PolynomialFeatureGenerator(target_columns=["temperature"], degrees=[2])
    ]
    
    # 3. Execute Cleaning & Engineering
    executor.execute_chain(ops)
    
    # 4. Feature Selection
    selection_ops = [
        VarianceThresholdSelector(metadata_list=executor.feature_metadata_registry, threshold=0.01, target_variable="target_yield"),
        MutualInformationSelector(metadata_list=executor.feature_metadata_registry, target_variable="target_yield", top_k=2),
        FeatureSelectionConsensus(metadata_list=executor.feature_metadata_registry, target_variable="target_yield", approval_threshold=0.5)
    ]
    
    result = executor.execute_chain(selection_ops)
    final_df = result["final_dataset"]
    
    pipeline_duration = time.time() - start_time
    
    # 5. Extract Metrics from Audit Trail
    print("\n--- Pipeline Execution Metrics ---")
    print(f"{'Operation':<35} | {'Exec Time (ms)':<15} | {'Memory (MB)':<12} | {'Rows/sec':<10}")
    print("-" * 80)
    
    total_mem = 0
    total_exec = 0
    for audit in result["audit_trail"]:
        res = audit.get("result", {})
        op_name = audit.get("operation_name", "Unknown")
        exec_ms = res.get("execution_time_ms", 0.0)
        mem_mb = res.get("memory_usage_mb", 0.0)
        rps = res.get("throughput_rows_per_sec", 0.0)
        
        total_exec += exec_ms
        total_mem = max(total_mem, mem_mb) # Peak memory tracking approximation
        
        print(f"{op_name:<35} | {exec_ms:<15.2f} | {mem_mb:<12.2f} | {rps:<10.0f}")
        
    print("-" * 80)
    print(f"{'Total Pipeline':<35} | {total_exec:<15.2f} | {total_mem:<12.2f} Peak")
    
    print("\n--- Quality Deltas ---")
    initial_q = result.get("initial_quality", {})
    final_q = result.get("final_quality", {})
    if initial_q and final_q:
        for k in initial_q.keys():
            diff = final_q.get(k, 0) - initial_q.get(k, 0)
            print(f"{k}: {initial_q.get(k, 0):.1f}% -> {final_q.get(k, 0):.1f}% ({'+' if diff>=0 else ''}{diff:.1f}%)")
    else:
        print("Quality scores not fully generated (mocked IDRS).")
        
    print(f"\nTotal End-to-End Duration: {pipeline_duration:.3f} seconds")
    
    print("\n--- Generating Reports & Visualizations ---")
    
    # Test Visualization Suite Generation
    viz_start = time.time()
    specs = VisualizationSpecificationGenerator.generate_suite_for_dataset(final_df, target_variable="target_yield")
    viz_time = time.time() - viz_start
    print(f"Generated {len(specs)} Visualization Specifications in {viz_time:.3f} seconds.")
    
    # Test Report Generation
    rep_start = time.time()
    summary = AnalyticsSummaryReportGenerator.generate(result, target_variable="target_yield")
    docs = AutoDocGenerator.generate_markdown()
    manifest = AnalyticsEngineManifestGenerator.generate()
    rep_time = time.time() - rep_start
    print(f"Generated 3 major reports/manifests in {rep_time:.3f} seconds.")
    
    print("\n=========================================================")
    print("          Benchmark Completed Successfully!              ")
    print("=========================================================")

if __name__ == "__main__":
    run_benchmark()
