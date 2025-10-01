import pandas as pd
from src.data.outliers import iqr_bounds, apply_outlier_policy


def test_iqr_bounds_monotonic(df_numeric_only):
    lo, hi = iqr_bounds(df_numeric_only["price"], k=1.5)
    assert lo < hi


def test_policy_filter_removes_outliers(df_numeric_only):
    out = apply_outlier_policy(df_numeric_only, "price", policy="filter", k=1.5)
    # Expect fewer rows after filtering (outlier removed)
    assert len(out) < len(df_numeric_only)
    assert out["price"].max() < df_numeric_only["price"].max()


def test_policy_clip_preserves_rows(df_numeric_only):
    out = apply_outlier_policy(df_numeric_only, "price", policy="clip", k=1.5)
    # Same number of rows
    assert len(out) == len(df_numeric_only)
    # No values beyond bounds
    lo, hi = iqr_bounds(df_numeric_only["price"], k=1.5)
    assert out["price"].between(lo, hi).all()


def test_policy_none_no_changes(df_numeric_only):
    out = apply_outlier_policy(df_numeric_only, "price", policy="none")
    pd.testing.assert_frame_equal(out, df_numeric_only)
