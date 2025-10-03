# tests/models/conftest.py
import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def df_features_minimal() -> pd.DataFrame:
    """
    Tiny synthetic dataset with a numeric target `price` and a few numeric features.
    Matches what the training pipeline expects (X = all columns except `price`).
    """
    rng = np.random.default_rng(0)
    n = 60
    df = pd.DataFrame(
        {
            "sqft_living": rng.integers(500, 3500, n),
            "bedrooms": rng.integers(1, 6, n),
            "bathrooms": rng.integers(1, 4, n),
            "lat": rng.uniform(47.0, 48.0, n),
            "long": rng.uniform(-122.5, -121.5, n),
        }
    )

    # price with a simple linear-ish relationship + noise
    price = (
        1000 * df["sqft_living"]
        + 20000 * df["bedrooms"]
        + 15000 * df["bathrooms"]
        + 5000 * (df["lat"] - 47.5)
        - 5000 * (df["long"] + 122.0)
        + rng.normal(0, 50000, n)
    )
    df["price"] = price.round(2)
    return df