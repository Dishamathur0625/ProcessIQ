import pandas as pd
from typing import Optional, List

class DateTimeProcessor:
    """
    Object-oriented datetime detection and processing module.
    Responsible for identifying time columns, converting them to standard formats,
    and inferring the industrial sampling frequency.
    """
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.datetime_col: Optional[str] = None
        
    def detect(self) -> Optional[str]:
        """Heuristic-based detection of datetime columns."""
        for col in self.df.columns:
            if 'time' in col.lower() or 'date' in col.lower():
                self.datetime_col = col
                return col
        return None
        
    def convert(self) -> pd.DataFrame:
        """Standardizes the datetime column and sets it as the index."""
        if not self.datetime_col:
            raise ValueError("No datetime column detected or specified.")
            
        self.df[self.datetime_col] = pd.to_datetime(self.df[self.datetime_col], errors='coerce')
        self.df.set_index(self.datetime_col, inplace=True)
        self.df.sort_index(inplace=True)
        return self.df
        
    def infer_frequency(self) -> Optional[str]:
        """Infers the sampling frequency of the dataset."""
        if self.df.index.name == self.datetime_col:
            # Drop NaNs to infer frequency accurately
            valid_index = self.df.index.dropna()
            if len(valid_index) > 1:
                return pd.infer_freq(valid_index)
        return None
        
    def process(self) -> dict:
        """Full datetime processing lifecycle."""
        self.detect()
        if self.datetime_col:
            self.convert()
            freq = self.infer_frequency()
            return {
                "datetime_column": self.datetime_col,
                "inferred_frequency": freq,
                "status": "success"
            }
        return {"status": "no_datetime_detected"}
