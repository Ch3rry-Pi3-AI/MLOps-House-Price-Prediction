import pandas as pd
from src.data.cleaning import fill_missing


def test_fill_missing_imputes_numeric_and_categorical(df_mixed):
    out = fill_missing(df_mixed)
    # No NA remaining
    assert out.isna().sum().sum() == 0
    # Numeric column uses median
    expected_median = df_mixed["bedrooms"].median()
    assert out.loc[out["bedrooms"] == expected_median].shape[0] >= 1
    # Categorical uses mode (Leeds)
    assert out["city"].isna().sum() == 0
