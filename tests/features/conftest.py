# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

import pandas as pd
import pytest
from datetime import datetime


# -------------------------------------------------------------------
# Fixtures for feature engineering
# -------------------------------------------------------------------

@pytest.fixture
def df_features_minimal() -> pd.DataFrame:
    """
    Minimal frame with all required columns for feature engineering.
    """
    return pd.DataFrame(
        {
            "price": [200000, 350000, 500000],
            "sqft": [1000, 1400, 2000],
            "bedrooms": [3, 4, 5],
            "bathrooms": [1, 2, 2],
            "year_built": [1990, 2005, 2015],
            "location": ["Leeds", "Manchester", "Leeds"],
            "condition": ["Good", "Fair", "Excellent"],
        }
    )


@pytest.fixture
def df_features_edge_cases() -> pd.DataFrame:
    """
    Includes division edge cases (bathrooms=0) and NaNs.
    """
    current_year = datetime.now().year
    return pd.DataFrame(
        {
            "price": [300000, 450000, 600000],
            "sqft": [1200, 0, 1500],  # zero sqft would create inf in price_per_sqft if used
            "bedrooms": [3, 4, 5],
            "bathrooms": [1, 0, 2],  # division by zero path
            "year_built": [current_year - 10, current_year - 20, current_year - 30],
            "location": ["Leeds", "Leeds", "Manchester"],
            "condition": ["Good", "Good", "Fair"],
        }
    )
