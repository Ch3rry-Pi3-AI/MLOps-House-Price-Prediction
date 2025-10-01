import logging
import pandas as pd

logger = logging.getLogger("data-schema")


def require_columns(df: pd.DataFrame, cols: list[str]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def is_numeric(series: pd.Series) -> bool:
    return pd.api.types.is_numeric_dtype(series)
