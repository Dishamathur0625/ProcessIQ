import pandas as pd
import numpy as np
from backend.engine.core.base_operation import BaseOperation

class PlantDataAligner(BaseOperation):
    """
    Detects and aligns raw plant data (stacked format) into a standard wide tabular format.
    If the dataset is already aligned, it performs necessary rounding on date_time.
    Implements the strict BaseOperation lifecycle.
    """
    def __init__(self):
        super().__init__()
        
    def _is_aligned_format(self, df: pd.DataFrame) -> bool:
        """Check if dataset is already in the aligned format (Task 1)."""
        if df.empty or len(df.columns) == 0:
            return False
            
        # Check if it was loaded with headers
        if str(df.columns[0]).strip() == "date_time":
            return True
            
        # Check if it was loaded without headers
        if str(df.iloc[0, 0]).strip() == "date_time":
            return True
            
        return False
        
    def _is_stacked_format(self, df: pd.DataFrame) -> bool:
        """Check if dataset is in the raw stacked format (Task 2)."""
        if df.shape[1] not in (2, 3):
            return False
            
        # In stacked data, column 0 contains both variable names (strings) and date-times.
        # Column 1 contains values, which are NaN on rows where column 0 is a variable name.
        col0 = df.iloc[:, 0]
        col1 = df.iloc[:, 1]
        
        # If there are rows where col1 is NaN but col0 is not NaN, these might be headers
        potential_headers = col1.isna() & col0.notna()
        if potential_headers.sum() > 0:
            # Check if there's a mix of dates and strings in col0
            # If so, it's very likely stacked plant data
            return True
            
        return False

    def validate(self, df: pd.DataFrame) -> bool:
        if df.empty:
            self.log_warning("Dataset is empty.")
            return False
        
        if self._is_aligned_format(df):
            self.log_info("Detected already aligned plant dataset.")
            return True
            
        if self._is_stacked_format(df):
            self.log_info("Detected stacked raw plant dataset.")
            return True
            
        return False
        
    def inspect(self, df: pd.DataFrame) -> dict:
        return {
            "initial_rows": len(df),
            "initial_columns": len(df.columns),
            "format": "aligned" if self._is_aligned_format(df) else "stacked"
        }
        
    def _process_aligned(self, df: pd.DataFrame) -> pd.DataFrame:
        self.log_info("Processing aligned dataset by rounding date_time to 2s intervals.")
        
        # If the headers are still in the first row, promote them
        if str(df.columns[0]).strip() != "date_time":
            df.columns = df.iloc[0]
            df = df[1:].reset_index(drop=True)
        
        if "date_time" in df.columns:
            df["date_time"] = pd.to_datetime(df["date_time"], errors="coerce")
            df["date_time"] = df["date_time"].dt.floor("2s")
            
        for col in df.columns:
            if col != "date_time":
                df[col] = pd.to_numeric(df[col], errors="coerce")
                
        return df

    def _process_stacked(self, df: pd.DataFrame) -> pd.DataFrame:
        self.log_info("Processing stacked dataset to align variables.")
        
        # 1. Check if the pandas column names are actually the first row of data
        # This happens because DatasetService saves it without header=None
        if any("Unnamed:" in str(c) for c in df.columns):
            import numpy as np
            # Create a row from the columns
            header_row = pd.DataFrame([df.columns], columns=df.columns)
            # Replace 'Unnamed: X' with NaN
            header_row = header_row.replace(regex=r'^Unnamed:.*', value=np.nan)
            df = pd.concat([header_row, df], ignore_index=True)
            
        # 2. Prepare columns
        if df.shape[1] == 2:
            df["register_id"] = None
            
        df = df.iloc[:, :3].copy()
        df.columns = ["date_or_variable", "value", "register_id"]
        
        # 3. Detect variable headers
        header_mask = (df["value"].isna() & df["date_or_variable"].notna())
        self.log_info(f"Variable headers detected: {header_mask.sum()}")
        
        # 4. Attach variable names
        df["variable"] = df["date_or_variable"].where(header_mask).ffill()
        
        # 5. Remove header rows
        data = df[~header_mask].copy()
        
        # 6. Convert date-time
        numeric_dates = pd.to_numeric(data["date_or_variable"], errors="coerce")
        if numeric_dates.notna().sum() > 0:
            data["date_time"] = pd.to_datetime(numeric_dates, unit="D", origin="1899-12-30", errors="coerce")
        else:
            data["date_time"] = pd.to_datetime(data["date_or_variable"], errors="coerce")
            
        # 7. Convert values to numeric
        data["value"] = pd.to_numeric(data["value"], errors="coerce")
        
        # 8. Create aligned dataframe
        final_df = data.pivot_table(
            index="date_time",
            columns="variable",
            values="value",
            aggfunc="first"
        ).reset_index()
        
        final_df.columns.name = None
        return final_df

    def execute(self, df: pd.DataFrame) -> pd.DataFrame:
        if self._is_aligned_format(df):
            return self._process_aligned(df)
        else:
            return self._process_stacked(df)
        
    def verify(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> bool:
        if df_after.empty:
            self.log_warning("Verification failed: Aligned dataset is empty.")
            return False
            
        if "date_time" not in df_after.columns:
            self.log_warning("Verification failed: Missing 'date_time' column in aligned dataset.")
            return False
            
        self.log_info(f"Verification passed: Output has {len(df_after)} rows and {len(df_after.columns)} columns.")
        return True
