# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.base import BaseEstimator

from src.features.builders import create_preprocessor, create_features


# -------------------------------------------------------------------
# Tests: create_preprocessor
# -------------------------------------------------------------------

def test_create_preprocessor_structure(df_features_minimal: pd.DataFrame):
    pre = create_preprocessor()
    assert isinstance(pre, ColumnTransformer)

    # Fit should succeed using engineered columns
    X = create_features(df_features_minimal).drop(columns=["price"])
    Xt = pre.fit_transform(X)

    # Expect a 2D matrix with rows preserved
    assert Xt.shape[0] == len(X)

    # Should be usable as a sklearn transformer
    assert hasattr(pre, "transform") and callable(pre.transform)


def test_preprocessor_handles_unseen_categories(df_features_minimal: pd.DataFrame):
    pre = create_preprocessor()
    X = create_features(df_features_minimal).drop(columns=["price"])
    pre.fit(X)

    # Transform a frame with unseen category values to ensure handle_unknown='ignore'
    X2 = X.copy()
    X2.loc[X2.index[0], "location"] = "Sheffield"  # unseen
    X2.loc[X2.index[1], "condition"] = "As-New"    # unseen

    Xt2 = pre.transform(X2)
    assert Xt2.shape[0] == len(X2)
