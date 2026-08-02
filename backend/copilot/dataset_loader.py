"""
Helpers to load / save job datasets through the configured storage backend.
Keeps the copilot endpoints storage-agnostic (local or supabase).
"""
import io
import pandas as pd

from backend.services.storage.factory import StorageFactory
from backend.core.config import settings


def load_job_dataframe(job_id: str, bucket: str = None, path: str = None) -> pd.DataFrame:
    storage = StorageFactory.get_backend()
    bucket = bucket or settings.SUPABASE_BUCKET_DATASETS
    path = path or f"{job_id}/dataset.csv"

    content_bytes = storage.download(bucket, path)
    if path.lower().endswith((".xlsx", ".xls")):
        return pd.read_excel(io.BytesIO(content_bytes))
    return pd.read_csv(io.BytesIO(content_bytes))


def save_job_dataframe(job_id: str, df: pd.DataFrame, bucket: str = None, path: str = None) -> str:
    storage = StorageFactory.get_backend()
    bucket = bucket or settings.SUPABASE_BUCKET_PROCESSED
    path = path or f"{job_id}/processed_dataset.csv"

    if path.lower().endswith((".xlsx", ".xls")):
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        storage.upload(bucket, path, io.BytesIO(excel_buffer.getvalue()))
    else:
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        storage.upload(bucket, path, io.BytesIO(csv_bytes))

    return f"{bucket}/{path}"
