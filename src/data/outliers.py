# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

import logging
import pandas as pd


# -------------------------------------------------------------------
# Logger setup
# -------------------------------------------------------------------

logger = logging.getLogger("data-outliers")


# -------------------------------------------------------------------
# Outlier detection
# -------------------------------------------------------------------

def iqr_bounds(series: pd.Series, k: float = 1.5) -> tuple[float, float]:
    """
    Compute lower and upper bounds for outlier detection using the IQR rule.

    Parameters
    ----------
    series : pd.Series
        Input numeric series.
    k : float, default=1.5
        IQR multiplier (controls whisker width).

    Returns
    -------
    tuple of float
        (lower_bound, upper_bound) for outlier detection.

    Notes
    -----
    Any values outside [lower_bound, upper_bound] are considered outliers
    under the standard Tukey boxplot rule.
    """

    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr


# -------------------------------------------------------------------
# Outlier handling
# -------------------------------------------------------------------

def apply_outlier_policy(
    df: pd.DataFrame,
    column: str,
    policy: str = "filter",
    k: float = 1.5,
) -> pd.DataFrame:
    """
    Apply an outlier handling policy to a given column.

    Parameters
    ----------
    df : pd.DataFrame
        Input dataset.
    column : str
        Name of the column to process.
    policy : {"filter", "clip", "none"}, default="filter"
        Outlier handling strategy:
        - "filter": Remove rows outside IQR bounds.
        - "clip": Cap values at IQR bounds.
        - "none": Leave values unchanged.
    k : float, default=1.5
        IQR multiplier for outlier bounds.

    Returns
    -------
    pd.DataFrame
        A new DataFrame with the selected outlier policy applied.

    Raises
    ------
    ValueError
        If `policy` is not one of {"filter", "clip", "none"}.

    Examples
    --------
    >>> df = pd.DataFrame({"x": [1, 2, 2, 3, 100]})
    >>> apply_outlier_policy(df, "x", policy="filter")
       x
    0  1
    1  2
    2  2
    3  3
    """

    if policy == "none":
        return df

    # Compute outlier thresholds
    lo, hi = iqr_bounds(df[column], k)
    mask = df[column].between(lo, hi)

    if policy == "filter":
        # Drop rows outside the bounds
        removed = (~mask).sum()
        if removed:
            logger.info(
                "Filtering %d outliers in %s (bounds=%.3f..%.3f)",
                removed,
                column,
                lo,
                hi,
            )
        return df.loc[mask].copy()

    if policy == "clip":
        # Cap values to the bounds
        logger.info("Clipping outliers in %s to bounds=%.3f..%.3f", column, lo, hi)
        out = df.copy()
        out[column] = out[column].clip(lo, hi)
        return out

    raise ValueError(f"Unknown outlier policy: {policy}")
