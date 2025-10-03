# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

import os
import sys

import numpy as np
import pandas as pd
import pytest


# -------------------------------------------------------------------
# Path shim (so `import src...` works)
# -------------------------------------------------------------------

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


# -------------------------------------------------------------------
# Fixtures
# -------------------------------------------------------------------

@pytest.fixture
def df_mixed() -> pd.DataFrame:
    """
    Small mixed-type DataFrame with some missing values.

    Features
    --------
    price : float
        Contains typical values (100,000-120,000), a NaN, and a high outlier.
    bedrooms : int
        Mixture of integers and missing values.
    city : str
        City names with one missing entry.

    Returns
    -------
    pd.DataFrame
        Test DataFrame with mixed dtypes and edge cases.
    """
    return pd.DataFrame(
        {
            "price": [100_000, 120_000, np.nan, 5_000_000],
            "bedrooms": [3, None, 2, 4],
            "city": ["Leeds", "Leeds", None, "Manchester"],
        }
    )


@pytest.fixture
def df_numeric_only() -> pd.DataFrame:
    """
    Simple numeric DataFrame with an obvious outlier.

    Features
    --------
    price : float
        Mostly clustered around 90-110 with one extreme value (10,000).

    Returns
    -------
    pd.DataFrame
        Numeric-only DataFrame for testing outlier handling.
    """
    return pd.DataFrame(
        {"price": [100, 105, 110, 90, 95, 10_000]}
    )
