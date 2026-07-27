import pandas as pd
import numpy as np
import os

def generate_benchmark_datasets():
    os.makedirs("datasets", exist_ok=True)
    
    np.random.seed(42)
    n_rows = 1000
    
    # 1. Clean Data
    df_clean = pd.DataFrame({
        "temperature": np.random.normal(50, 5, n_rows),
        "pressure": np.random.normal(100, 10, n_rows),
        "vibration": np.random.normal(5, 1, n_rows)
    })
    df_clean.to_csv("datasets/clean_data.csv", index=False)
    
    # 2. Missing Data (30% missing in temperature)
    df_missing = df_clean.copy()
    missing_indices = np.random.choice(n_rows, size=int(0.3 * n_rows), replace=False)
    df_missing.loc[missing_indices, "temperature"] = np.nan
    df_missing.to_csv("datasets/missing_data.csv", index=False)
    
    # 3. Duplicate Data (15% exact duplicates)
    df_duplicates = pd.concat([df_clean, df_clean.sample(frac=0.15, random_state=42)], ignore_index=True)
    df_duplicates.to_csv("datasets/duplicate_data.csv", index=False)
    
    # 4. Outlier Data (5% extreme values in pressure)
    df_outliers = df_clean.copy()
    outlier_indices = np.random.choice(n_rows, size=int(0.05 * n_rows), replace=False)
    df_outliers.loc[outlier_indices, "pressure"] = np.random.uniform(200, 300, size=len(outlier_indices))
    df_outliers.to_csv("datasets/outlier_data.csv", index=False)
    
    # 5. Timeseries Data (with gaps for forward fill)
    date_rng = pd.date_range(start='2026-01-01', periods=n_rows, freq='h')
    df_ts = pd.DataFrame({
        "timestamp": date_rng,
        "sensor_reading": np.sin(np.linspace(0, 50, n_rows)) + np.random.normal(0, 0.1, n_rows)
    })
    # Add gaps
    gap_indices = np.random.choice(n_rows, size=int(0.1 * n_rows), replace=False)
    df_ts.loc[gap_indices, "sensor_reading"] = np.nan
    df_ts.to_csv("datasets/timeseries_data.csv", index=False)
    
    print("Benchmark datasets generated successfully in 'datasets/' directory.")

if __name__ == "__main__":
    generate_benchmark_datasets()
