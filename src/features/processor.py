# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

import logging
from pathlib import Path
import pickle
import pandas as pd

from .builders import create_features, create_preprocessor


# -------------------------------------------------------------------
# Logger setup
# -------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("feature-pipeline")


# -------------------------------------------------------------------
# End-to-end feature engineering runner
# -------------------------------------------------------------------

def run_feature_engineering(
    input_file: str | Path,
    output_file: str | Path,
    preprocessor_file: str | Path = "models/trained/preprocessor.pkl",
) -> pd.DataFrame:
    """
    Full feature engineering pipeline.

    Parameters
    ----------
    input_file : str or Path
        Path to cleaned CSV file.
    output_file : str or Path
        Path for output CSV file (engineered features).
    preprocessor_file : str or Path, default="models/trained/preprocessor.pkl"
        Path for saving the fitted preprocessor with pickle.
    """
    # Load cleaned data
    logger.info("Loading data from %s", input_file)
    df = pd.read_csv(input_file)

    # Create features
    df_featured = create_features(df)
    logger.info("Created featured dataset with shape: %s", df_featured.shape)

    # Create and fit the preprocessor
    preprocessor = create_preprocessor()
    X = df_featured.drop(columns=["price"], errors="ignore")
    y = df_featured["price"] if "price" in df_featured.columns else None
    X_transformed = preprocessor.fit_transform(X)
    logger.info("Fitted the preprocessor and transformed the features")

    # Ensure models/trained folder exists
    preprocessor_file = Path(preprocessor_file)
    preprocessor_file.parent.mkdir(parents=True, exist_ok=True)

    # Save the preprocessor with pickle
    with open(preprocessor_file, "wb") as f:
        pickle.dump(preprocessor, f)
    logger.info("Saved preprocessor to %s", preprocessor_file)

    # Save fully preprocessed data
    output_file = Path(output_file)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    df_transformed = pd.DataFrame(X_transformed)
    if y is not None:
        df_transformed["price"] = y.values
    df_transformed.to_csv(output_file, index=False)
    logger.info("Saved fully preprocessed data to %s", output_file)

    return df_transformed


# -------------------------------------------------------------------
# Minimal script entry point
# -------------------------------------------------------------------

if __name__ == "__main__":
    run_feature_engineering(
        "data/processed/cleaned_house_data.csv",
        "data/processed/engineered_features.csv",
        "models/trained/preprocessor.pkl",
    )
