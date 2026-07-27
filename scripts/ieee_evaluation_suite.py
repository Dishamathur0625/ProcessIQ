import pandas as pd
import numpy as np
import time
import os
import psutil
from backend.engine.core.pipeline_executor import PipelineExecutor
from backend.engine.cleaning.imputation.mean_imputation import MeanImputation
from backend.engine.features.general.polynomial_generator import PolynomialFeatureGenerator
from backend.engine.features.timeseries.lag_generator import LagFeatureGenerator
from backend.engine.features.categorical.one_hot_generator import OneHotEncoderGenerator
from backend.engine.selection.variance_selector import VarianceThresholdSelector
from backend.engine.selection.mutual_info_selector import MutualInformationSelector
from backend.engine.selection.consensus_engine import FeatureSelectionConsensus

def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024 * 1024)

class DatasetGenerator:
    @staticmethod
    def clean_tabular(rows=10000):
        np.random.seed(42)
        return pd.DataFrame({
            "target": np.random.randn(rows),
            "f1": np.random.randn(rows),
            "f2": np.random.randn(rows) * 5,
            "f3": np.random.randn(rows) * 10
        }), "clean_tabular", ["f1", "f2"]

    @staticmethod
    def missing_heavy(rows=10000):
        df, name, num_cols = DatasetGenerator.clean_tabular(rows)
        # Inject 30% missing in f1
        mask = np.random.rand(rows) < 0.3
        df.loc[mask, "f1"] = np.nan
        return df, "missing_heavy", num_cols

    @staticmethod
    def high_cardinality(rows=10000):
        df, name, num_cols = DatasetGenerator.clean_tabular(rows)
        df["cat_high"] = np.random.choice([f"cat_{i}" for i in range(500)], size=rows)
        return df, "high_cardinality", num_cols

    @staticmethod
    def time_series(rows=10000):
        np.random.seed(42)
        dates = pd.date_range("2023-01-01", periods=rows, freq="h")
        return pd.DataFrame({
            "timestamp": dates,
            "sensor1": np.sin(np.linspace(0, 50, rows)) + np.random.randn(rows)*0.1,
            "target": np.cos(np.linspace(0, 50, rows))
        }), "time_series", ["sensor1"]

    @staticmethod
    def skewed(rows=10000):
        np.random.seed(42)
        return pd.DataFrame({
            "target": np.random.randn(rows),
            "f1": np.random.lognormal(mean=0, sigma=2, size=rows), # Highly right skewed
            "f2": np.random.randn(rows)
        }), "skewed", ["f1"]

    @staticmethod
    def wide(rows=1000, cols=200):
        np.random.seed(42)
        data = {f"f{i}": np.random.randn(rows) for i in range(cols)}
        data["target"] = np.random.randn(rows)
        return pd.DataFrame(data), "wide", ["f0", "f1"]

    @staticmethod
    def tall(rows=500000):
        # 500k rows
        return DatasetGenerator.clean_tabular(rows=rows)[0], "tall", ["f1", "f2"]

    @staticmethod
    def mixed_industrial(rows=10000):
        np.random.seed(42)
        df = pd.DataFrame({
            "target": np.random.randn(rows),
            "temperature": np.random.randn(rows) * 10 + 150,
            "pressure": np.random.randn(rows) * 5 + 30,
            "machine_id": np.random.choice(["M1", "M2", "M3"], size=rows),
            "status_code": np.random.choice(["OK", "WARN", "ERR"], size=rows)
        })
        # Inject missing
        df.loc[:1000, "temperature"] = np.nan
        return df, "mixed_industrial", ["temperature", "pressure"]

def run_ieee_benchmark():
    datasets = [
        DatasetGenerator.clean_tabular(),
        DatasetGenerator.missing_heavy(),
        DatasetGenerator.high_cardinality(),
        DatasetGenerator.time_series(),
        DatasetGenerator.skewed(),
        DatasetGenerator.wide(),
        DatasetGenerator.tall(),
        DatasetGenerator.mixed_industrial()
    ]
    
    results = []
    
    print("==========================================================================================")
    print("                  ProcessIQ Analytics Engine - IEEE Evaluation Suite                      ")
    print("==========================================================================================")
    print(f"{'Dataset Type':<20} | {'Rows':<8} | {'Cols':<5} | {'Exec (ms)':<10} | {'RAM (MB)':<10} | {'Rows/sec':<10} | {'IDRS Delta':<8}")
    print("-" * 90)
    
    for df, name, num_cols in datasets:
        rows = len(df)
        cols = len(df.columns)
        
        executor = PipelineExecutor(df)
        
        ops = [
            MeanImputation(target_columns=num_cols),
            PolynomialFeatureGenerator(target_columns=num_cols[:1], degrees=[2]),
            VarianceThresholdSelector(metadata_list=[], target_variable="target", threshold=0.01),
            MutualInformationSelector(metadata_list=[], target_variable="target", top_k=5)
        ]
        
        # Link metadata for selectors
        ops[2].metadata_list = executor.feature_metadata_registry
        ops[3].metadata_list = executor.feature_metadata_registry
        
        # Additional ops for specific types
        if name == "time_series":
            ops.insert(1, LagFeatureGenerator(target_columns=["sensor1"], lags=[1, 2]))
        elif name == "mixed_industrial":
            ops.insert(1, OneHotEncoderGenerator(target_columns=["machine_id", "status_code"]))
            
        start_mem = get_memory_usage()
        start_time = time.time()
        
        res = executor.execute_chain(ops)
        
        end_time = time.time()
        peak_mem = get_memory_usage() - start_mem
        exec_ms = (end_time - start_time) * 1000
        throughput = rows / (end_time - start_time) if end_time > start_time else 0
        
        initial_idrs = res.get("initial_quality", {}).get("industrial_dataset_readiness", 0)
        final_idrs = res.get("final_quality", {}).get("industrial_dataset_readiness", 0)
        idrs_delta = final_idrs - initial_idrs
        
        print(f"{name:<20} | {rows:<8} | {cols:<5} | {exec_ms:<10.1f} | {peak_mem:<10.1f} | {throughput:<10.0f} | {idrs_delta:+.1f}%")
        
        results.append({
            "Dataset Type": name,
            "Rows": rows,
            "Columns": cols,
            "Execution Time (ms)": exec_ms,
            "Peak Memory (MB)": peak_mem,
            "Throughput (rows/sec)": throughput,
            "IDRS Delta (%)": idrs_delta
        })
        
    print("==========================================================================================")
    
    # Save markdown report
    md = ["# ProcessIQ IEEE Evaluation Suite Results\n"]
    md.append("This document presents the quantitative benchmark results for the ProcessIQ Analytics Engine across various dataset typologies.\n")
    md.append(pd.DataFrame(results).to_markdown(index=False))
    
    with open("ieee_evaluation_report.md", "w") as f:
        f.write("\n".join(md))
        
    print("Results saved to ieee_evaluation_report.md")

if __name__ == "__main__":
    run_ieee_benchmark()
