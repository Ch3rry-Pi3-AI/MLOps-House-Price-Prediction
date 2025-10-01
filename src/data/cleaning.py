import logging
import pandas as pd
from .schema import is_numeric

logger = logging.getLogger("data-cleaning")


def fill_missing(df: pd.DataFrame) -> pd.DataFrame:
    """Impute numeric with median; categorical with mode."""
    out = df.copy()
    for col in out.columns:
        miss = out[col].isna().sum()
        if miss == 0:
            continue
        if is_numeric(out[col]):
            med = out[col].median()
            out[col] = out[col].fillna(med)
            logger.info("Filled %d NA in %s with median=%s", miss, col, med)
        else:
            mode = out[col].mode(dropna=True)
            if not mode.empty:
                val = mode.iloc[0]
                out[col] = out[col].fillna(val)
                logger.info("Filled %d NA in %s with mode=%s", miss, col, val)
            else:
                out[col] = out[col].fillna("UNKNOWN")
                logger.info("Filled %d NA in %s with 'UNKNOWN'", miss, col)
    return out
