"""
Deterministic Exploratory Data Analysis (EDA) statistics.

Computes per-column and dataset-level statistics using plain pandas/numpy so the
values are fully reproducible and can be rendered in the dashboard next to the
LLM's narrative. This mirrors what a data analyst would run interactively
(df.describe(), df.mode(), df.skew(), ...).
"""
import numpy as np
import pandas as pd
from typing import Any, Dict, List


def _serialize(value: Any) -> Any:
    """Convert numpy/pandas scalars to native Python types for JSON."""
    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    if isinstance(value, np.ndarray):
        return [_serialize(v) for v in value.tolist()]
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, pd.Series):
        return [_serialize(v) for v in value.tolist()]
    if isinstance(value, dict):
        return {k: _serialize(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_serialize(v) for v in value]
    return value


def _mode_of(series: pd.Series) -> List[Any]:
    """Return the mode(s) of a series as a serializable list (empty if none)."""
    try:
        modes = series.mode(dropna=True)
    except Exception:
        return []
    return [_serialize(m) for m in modes.tolist()]


def column_eda_stats(series: pd.Series) -> Dict[str, Any]:
    """
    Compute descriptive statistics for a single column.
    Numeric columns get mean/median/mode/std/quantiles/skew/kurtosis, etc.
    Non-numeric columns get cardinality/top/freq plus a numeric profile when
    the values are coercible to numbers.
    """
    stats: Dict[str, Any] = {
        "dtype": str(series.dtype),
        "count": int(series.count()),
        "nulls": int(series.isna().sum()),
        "null_pct": round(float(series.isna().mean()), 4) if len(series) else 0.0,
    }

    if series.empty:
        return stats

    is_numeric = pd.api.types.is_numeric_dtype(series)

    # Object columns may still hold numbers (e.g. "1,000", "5") - try to coerce.
    numeric_view = series
    if not is_numeric and series.dtype == object:
        coerced = pd.to_numeric(series, errors="coerce")
        if coerced.notna().sum() >= max(1, int(0.6 * series.count())):
            numeric_view = coerced
            stats["numeric_coerced"] = True

    if pd.api.types.is_datetime64_any_dtype(series):
        stats["min"] = _serialize(series.min())
        stats["max"] = _serialize(series.max())
        stats["unique"] = int(series.nunique())
        return stats

    if is_numeric or "numeric_coerced" in stats:
        clean = numeric_view.dropna()
        stats.update({
            "mean": _serialize(clean.mean()),
            "median": _serialize(clean.median()),
            "mode": _mode_of(clean),
            "std": _serialize(clean.std()),
            "variance": _serialize(clean.var()),
            "min": _serialize(clean.min()),
            "max": _serialize(clean.max()),
            "q1": _serialize(clean.quantile(0.25)),
            "q2": _serialize(clean.quantile(0.50)),
            "q3": _serialize(clean.quantile(0.75)),
            "iqr": _serialize(clean.quantile(0.75) - clean.quantile(0.25)),
            "range": _serialize(clean.max() - clean.min()),
            "skew": _serialize(clean.skew()),
            "kurtosis": _serialize(clean.kurtosis()),
        })
    else:
        stats.update({
            "unique": int(series.nunique()),
            "top": _serialize(series.mode(dropna=True).iloc[0]) if series.mode(dropna=True).size else None,
            "freq": int(series.mode(dropna=True).iloc[0] and series.value_counts().iloc[0]) if series.value_counts().size else 0,
        })
    return stats


def compute_eda_stats(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Compute a full EDA summary for a dataframe:

    - overview: shape, duplicate rows, missing cells, dtype mix
    - columns: per-column statistics (mean, median, mode, std, quantiles, ...)
    """
    n_rows, n_cols = df.shape

    numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
    object_cols = [c for c in df.columns if df[c].dtype == object]
    dt_cols = [c for c in df.columns if pd.api.types.is_datetime64_any_dtype(df[c])]

    overview = {
        "rows": n_rows,
        "columns": n_cols,
        "numeric_columns": len(numeric_cols),
        "categorical_columns": len(object_cols),
        "datetime_columns": len(dt_cols),
        "duplicate_rows": int(df.duplicated().sum()),
        "total_missing_cells": int(df.isna().sum().sum()),
        "missing_cell_pct": round(float(df.isna().mean().mean()), 4) if n_rows and n_cols else 0.0,
        "memory_kb": round(float(df.memory_usage(deep=True).sum()) / 1024.0, 2),
    }

    columns = {str(col): column_eda_stats(df[col]) for col in df.columns}

    return {"overview": overview, "columns": columns}
