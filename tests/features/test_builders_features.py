# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

import pandas as pd
import numpy as np
from datetime import datetime

from src.features.builders import create_features


# -------------------------------------------------------------------
# Tests: create_features
# -------------------------------------------------------------------

def test_create_features_adds_expected_columns(df_features_minimal: pd.DataFrame):
    out = create_features(df_features_minimal)

    # New columns exist
    for col in ["house_age", "price_per_sqft", "bed_bath_ratio"]:
        assert col in out.columns, f"Expected engineered column '{col}'."

    # Original is not modified in-place
    assert "house_age" not in df_features_minimal.columns

    # house_age is computed as current_year - year_built
    current_year = datetime.now().year
    expected = current_year - df_features_minimal["year_built"]
    pd.testing.assert_series_equal(out["house_age"], expected, check_names=False)

    # price_per_sqft = price / sqft (finite for non-zero sqft)
    mask = df_features_minimal["sqft"] != 0
    assert np.isfinite(out.loc[mask, "price_per_sqft"]).all()


def test_create_features_handles_division_edge_cases(df_features_edge_cases: pd.DataFrame):
    out = create_features(df_features_edge_cases)

    # bed_bath_ratio should not contain inf/-inf and NaNs are filled with 0
    assert np.isfinite(out["bed_bath_ratio"]).all()
    assert out["bed_bath_ratio"].isna().sum() == 0

    # If bathrooms == 0 then ratio should be 0 after cleaning
    zero_bath_rows = df_features_edge_cases["bathrooms"] == 0
    assert (out.loc[zero_bath_rows, "bed_bath_ratio"] == 0).all()
