import pandas as pd
from typing import List
from backend.engine.features.base_feature_generator import BaseFeatureGenerator

class RollingStatisticsGenerator(BaseFeatureGenerator):
    """
    Generates rolling window statistics (mean, std, max, min).
    """
    def __init__(self, target_columns: List[str], windows: List[int] = [3], stats: List[str] = ['mean']):
        super().__init__(target_columns)
        self.windows = windows
        self.stats = stats # Allowed: 'mean', 'std', 'max', 'min'
        
    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty or not self.target_columns:
            return False
        for col in self.target_columns:
            if col not in df.columns:
                self.log_warning(f"Target column {col} not found in dataset.")
                return False
        for stat in self.stats:
            if stat not in ['mean', 'std', 'max', 'min']:
                self.log_warning(f"Statistic '{stat}' is not supported.")
                return False
        return True
        
    def inspect(self, df: pd.DataFrame) -> dict:
        expected_features = len(self.target_columns) * len(self.windows) * len(self.stats)
        self.log_info(f"Will generate {expected_features} rolling statistic features.")
        return {"expected_features": expected_features, "windows": self.windows, "stats": self.stats}
        
    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        df_new = df.copy()
        
        for col in self.target_columns:
            for window in self.windows:
                rolling_view = df_new[col].rolling(window=window)
                
                if 'mean' in self.stats:
                    new_col_name = f"{col}_rolling_{window}_mean"
                    df_new[new_col_name] = rolling_view.mean()
                    self._create_metadata(new_col_name, [col], f"rolling({window}).mean()")
                    
                if 'std' in self.stats:
                    new_col_name = f"{col}_rolling_{window}_std"
                    df_new[new_col_name] = rolling_view.std()
                    self._create_metadata(new_col_name, [col], f"rolling({window}).std()")
                    
                if 'max' in self.stats:
                    new_col_name = f"{col}_rolling_{window}_max"
                    df_new[new_col_name] = rolling_view.max()
                    self._create_metadata(new_col_name, [col], f"rolling({window}).max()")
                    
                if 'min' in self.stats:
                    new_col_name = f"{col}_rolling_{window}_min"
                    df_new[new_col_name] = rolling_view.min()
                    self._create_metadata(new_col_name, [col], f"rolling({window}).min()")
                    
        return df_new
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        expected_features = len(self.target_columns) * len(self.windows) * len(self.stats)
        actual_new_features = len(df_after.columns) - len(df_before.columns)
        
        if actual_new_features != expected_features:
            self.log_warning(f"Verification failed: Expected {expected_features} new features, got {actual_new_features}.")
            return False
        return True
