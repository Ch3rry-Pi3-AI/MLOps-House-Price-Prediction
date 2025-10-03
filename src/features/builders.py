# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

import logging
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer


# -------------------------------------------------------------------
# Logger setup
# -------------------------------------------------------------------

logger = logging.getLogger("feature-engineering")


# -------------------------------------------------------------------
# Public builders 
# -------------------------------------------------------------------

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create new features from existing data.

    Notes
    -----
    Logic preserved exactly from the original engineer.py.
    """
    logger.info("Creating new features")

    # Make a copy to avoid modifying the original dataframe
    df_featured = df.copy()

    # Calculate house age
    current_year = datetime.now().year
    df_featured["house_age"] = current_year - df_featured["year_built"]
    logger.info("Created 'house_age' feature")

    # Price per square foot
    df_featured["price_per_sqft"] = df_featured["price"] / df_featured["sqft"]
    logger.info("Created 'price_per_sqft' feature")

    # Bedroom to bathroom ratio
    df_featured["bed_bath_ratio"] = df_featured["bedrooms"] / df_featured["bathrooms"]
    # Handle division by zero
    df_featured["bed_bath_ratio"] = df_featured["bed_bath_ratio"].replace(
        [np.inf, -np.inf], np.nan
    )
    df_featured["bed_bath_ratio"] = df_featured["bed_bath_ratio"].fillna(0)
    logger.info("Created 'bed_bath_ratio' feature")

    # Do NOT one-hot encode categorical variables here; let the preprocessor handle it
    return df_featured


def create_preprocessor() -> ColumnTransformer:
    """
    Create a preprocessing pipeline.

    Notes
    -----
    Logic preserved exactly from the original engineer.py.
    """
    logger.info("Creating preprocessor pipeline")

    # Define feature groups 
    categorical_features = ["location", "condition"]
    numerical_features = [
        "sqft",
        "bedrooms",
        "bathrooms",
        "house_age",
        "price_per_sqft",
        "bed_bath_ratio",
    ]

    # Preprocessing for numerical features
    numerical_transformer = Pipeline(steps=[("imputer", SimpleImputer(strategy="mean"))])

    # Preprocessing for categorical features
    categorical_transformer = Pipeline(
        steps=[("onehot", OneHotEncoder(handle_unknown="ignore"))]
    )

    # Combine preprocessors in a column transformer
    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numerical_transformer, numerical_features),
            ("cat", categorical_transformer, categorical_features),
        ]
    )

    return preprocessor