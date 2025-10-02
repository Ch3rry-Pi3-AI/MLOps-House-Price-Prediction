# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

import logging
import pandas as pd
from .schema import is_numeric


# -------------------------------------------------------------------
# Logger setup
# -------------------------------------------------------------------

logger = logging.getLogger("data-cleaning")


# -------------------------------------------------------------------
# Missing value imputation
# -------------------------------------------------------------------

def fill_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Fill missing values in a DataFrame.

    - Numeric columns are imputed with the median.
    - Categorical columns are imputed with the mode (or 'UNKNOWN' if no mode).

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with potential missing values.

    Returns
    -------
    pd.DataFrame
        Copy of the DataFrame with imputed values.
    """

    out = df.copy()

    for col in out.columns:
        miss = out[col].isna().sum()
        if miss == 0:
            continue  # Skip columns with no missing values

        if is_numeric(out[col]):
            # Numeric → median
            med = out[col].median()
            out[col] = out[col].fillna(med)
            logger.info("Filled %d NA in %s with median=%s", miss, col, med)
        else:
            # Categorical → mode (if exists), otherwise 'UNKNOWN'
            mode = out[col].mode(dropna=True)
            if not mode.empty:
                val = mode.iloc[0]
                out[col] = out[col].fillna(val)
                logger.info("Filled %d NA in %s with mode=%s", miss, col, val)
            else:
                out[col] = out[col].fillna("UNKNOWN")
                logger.info("Filled %d NA in %s with 'UNKNOWN'", miss, col)

    return out
