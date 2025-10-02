# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

import pandas as pd

from src.data.outliers import iqr_bounds, apply_outlier_policy


# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------

def test_iqr_bounds_monotonic(df_numeric_only: pd.DataFrame):
    """
    Verify that IQR bounds are ordered correctly.
    
    Expectation: lower bound < upper bound.
    """
    lo, hi = iqr_bounds(df_numeric_only["price"], k=1.5)
    assert lo < hi


def test_policy_filter_removes_outliers(df_numeric_only: pd.DataFrame):
    """
    Verify that the 'filter' policy removes rows with values outside IQR bounds.

    Expectations
    ------------
    - Output has fewer rows than input.
    - Maximum value in output is smaller than in the input (outlier removed).
    """
    out = apply_outlier_policy(df_numeric_only, "price", policy="filter", k=1.5)
    assert len(out) < len(df_numeric_only)
    assert out["price"].max() < df_numeric_only["price"].max()


def test_policy_clip_preserves_rows(df_numeric_only: pd.DataFrame):
    """
    Verify that the 'clip' policy caps values at IQR bounds but preserves row count.

    Expectations
    ------------
    - Row count is unchanged.
    - All values are within computed IQR bounds.
    """
    out = apply_outlier_policy(df_numeric_only, "price", policy="clip", k=1.5)
    assert len(out) == len(df_numeric_only)

    lo, hi = iqr_bounds(df_numeric_only["price"], k=1.5)
    assert out["price"].between(lo, hi).all()


def test_policy_none_no_changes(df_numeric_only: pd.DataFrame):
    """
    Verify that the 'none' policy leaves the DataFrame unchanged.
    """
    out = apply_outlier_policy(df_numeric_only, "price", policy="none")
    pd.testing.assert_frame_equal(out, df_numeric_only)
