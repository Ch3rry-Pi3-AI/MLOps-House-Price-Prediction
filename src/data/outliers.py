import logging
import pandas as pd

logger = logging.getLogger("data-outliers")


def iqr_bounds(series: pd.Series, k: float = 1.5) -> tuple[float, float]:
    q1, q3 = series.quantile(0.25), series.quantile(0.75)
    iqr = q3 - q1
    return q1 - k * iqr, q3 + k * iqr


def apply_outlier_policy(
    df: pd.DataFrame, column: str, policy: str = "filter", k: float = 1.5
) -> pd.DataFrame:
    if policy == "none":
        return df

    lo, hi = iqr_bounds(df[column], k)
    mask = df[column].between(lo, hi)

    if policy == "filter":
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
        logger.info("Clipping outliers in %s to bounds=%.3f..%.3f", column, lo, hi)
        out = df.copy()
        out[column] = out[column].clip(lo, hi)
        return out

    raise ValueError(f"Unknown outlier policy: {policy}")
