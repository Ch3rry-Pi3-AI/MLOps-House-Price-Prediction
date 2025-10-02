# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

import logging
import pandas as pd


# -------------------------------------------------------------------
# Logger setup
# -------------------------------------------------------------------

logger = logging.getLogger("data-schema")


# -------------------------------------------------------------------
# Schema validation
# -------------------------------------------------------------------

def require_columns(df: pd.DataFrame, cols: list[str]) -> None:
    """
    Ensure that the DataFrame contains all required columns.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset.
    cols : list of str
        List of required column names.

    Raises
    ------
    ValueError
        If one or more required columns are missing.
    """

    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


# -------------------------------------------------------------------
# Column type checks
# -------------------------------------------------------------------

def is_numeric(series: pd.Series) -> bool:
    """
    Check if a pandas Series is numeric.

    Parameters
    ----------
    series : pd.Series
        Input series.

    Returns
    -------
    bool
        True if the series has a numeric dtype, False otherwise.
    """

    return pd.api.types.is_numeric_dtype(series)
