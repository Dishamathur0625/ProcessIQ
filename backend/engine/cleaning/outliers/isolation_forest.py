import pandas as pd
from sklearn.ensemble import IsolationForest
from backend.engine.core.base_operation import BaseOperation

class IsolationForestDetector(BaseOperation):
    """
    Detects and removes anomalies using Isolation Forest.
    """
    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        super().__init__()
        self.contamination = contamination
        self.random_state = random_state
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty:
            return False
        numeric_cols = df.select_dtypes(include='number').columns
        if len(numeric_cols) == 0:
            self.log_warning("No numeric columns found for outlier detection.")
            return False
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        return {"shape_before": df.shape}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        self.log_info(f"Running Isolation Forest (contamination={self.contamination})...")
        numeric_df = df.select_dtypes(include='number').dropna() # IF doesn't handle NaNs by default
        
        if numeric_df.empty:
            self.log_warning("Numeric dataset is empty after dropping NaNs. Returning original df.")
            return df
            
        model = IsolationForest(contamination=self.contamination, random_state=self.random_state)
        # 1 means normal, -1 means anomaly
        preds = model.fit_predict(numeric_df)
        
        # Align predictions back to the original dataframe
        df_clean = df.loc[numeric_df.index[preds == 1]]
        
        anomalies_removed = len(df) - len(df_clean)
        self.log_info(f"Removed {anomalies_removed} anomalous rows.")
        return df_clean
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        if len(df_after) > len(df_before):
            self.log_warning("Verification failed: Output dataset is larger than input.")
            return False
        self.log_info(f"Verification passed: Final dataset shape is {df_after.shape}")
        return True
