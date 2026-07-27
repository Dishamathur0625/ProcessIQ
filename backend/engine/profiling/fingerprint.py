import pandas as pd
import hashlib
import json
from typing import Dict, Any

class DatasetFingerprint:
    """
    Generates an immutable identity for a dataset based on its schema, types, sampling, and statistics.
    Used for caching, duplication detection, and research reproducibility.
    """
    
    @staticmethod
    def generate(df: pd.DataFrame, metadata: Dict[str, Any] = None) -> str:
        if df.empty:
            return "empty_dataset"
            
        fingerprint_data = {
            "schema_hash": DatasetFingerprint._hash_schema(df),
            "types_hash": DatasetFingerprint._hash_types(df),
            "stats_hash": DatasetFingerprint._hash_statistics(df),
            "metadata_hash": DatasetFingerprint._hash_metadata(metadata)
        }
        
        # Combine all component hashes into a master fingerprint
        master_string = json.dumps(fingerprint_data, sort_keys=True)
        return hashlib.sha256(master_string.encode('utf-8')).hexdigest()
        
    @staticmethod
    def _hash_schema(df: pd.DataFrame) -> str:
        columns = list(df.columns)
        return hashlib.md5(json.dumps(columns).encode('utf-8')).hexdigest()
        
    @staticmethod
    def _hash_types(df: pd.DataFrame) -> str:
        dtypes = {col: str(dtype) for col, dtype in df.dtypes.items()}
        return hashlib.md5(json.dumps(dtypes, sort_keys=True).encode('utf-8')).hexdigest()
        
    @staticmethod
    def _hash_statistics(df: pd.DataFrame) -> str:
        # Take a robust statistical snapshot (e.g., mean of numeric columns, missing counts)
        numeric_df = df.select_dtypes(include='number')
        stats = {}
        if not numeric_df.empty:
            stats["means"] = numeric_df.mean().round(4).to_dict()
        stats["missing"] = df.isna().sum().to_dict()
        stats["shape"] = df.shape
        return hashlib.md5(json.dumps(stats, sort_keys=True).encode('utf-8')).hexdigest()
        
    @staticmethod
    def _hash_metadata(metadata: Dict[str, Any]) -> str:
        if not metadata:
            return "no_metadata"
        return hashlib.md5(json.dumps(metadata, sort_keys=True).encode('utf-8')).hexdigest()
