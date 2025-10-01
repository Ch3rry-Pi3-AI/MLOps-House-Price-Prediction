import os, sys
import pandas as pd
import numpy as np
import pytest

# 👇 Path shim so "import src..." works
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture
def df_mixed():
    """Small mixed-type DataFrame with some missing values."""
    return pd.DataFrame(
        {
            "price": [
                100_000,
                120_000,
                np.nan,
                5_000_000,
            ],  # includes NaN and an outlier
            "bedrooms": [3, None, 2, 4],
            "city": ["Leeds", "Leeds", None, "Manchester"],
        }
    )


@pytest.fixture
def df_numeric_only():
    """Simple numeric DataFrame with an obvious outlier."""
    return pd.DataFrame({"price": [100, 105, 110, 90, 95, 10_000]})
