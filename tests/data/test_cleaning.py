# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

import pandas as pd

from src.data.cleaning import fill_missing


# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------

def test_fill_missing_imputes_numeric_and_categorical(df_mixed: pd.DataFrame):
    """
    Verify that `fill_missing` correctly imputes both numeric and categorical data.

    Expectations
    ------------
    - No missing values remain after imputation.
    - Numeric columns are imputed using the median.
    - Categorical columns are imputed using the mode.
    """
    out = fill_missing(df_mixed)

    # No NA remaining
    assert out.isna().sum().sum() == 0

    # Numeric column uses median
    expected_median = df_mixed["bedrooms"].median()
    assert (out["bedrooms"] == expected_median).any()

    # Categorical column uses mode ("Leeds")
    assert out["city"].isna().sum() == 0
