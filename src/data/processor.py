# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

import logging
from pathlib import Path
import pandas as pd

from .config import ProcessorConfig
from .io import load_csv, save_csv
from .schema import require_columns
from .cleaning import fill_missing
from .outliers import apply_outlier_policy


# -------------------------------------------------------------------
# Logger setup
# -------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("data-processor")


# -------------------------------------------------------------------
# Main data processing pipeline
# -------------------------------------------------------------------

def process_data(
    input_file: str,
    output_file: str,
    config: ProcessorConfig = ProcessorConfig(),
) -> pd.DataFrame:
    """
    End-to-end data preprocessing pipeline.

    Steps:
    1. Load raw CSV.
    2. Validate required columns.
    3. Impute missing values.
    4. Apply outlier handling.
    5. Save cleaned dataset.

    Parameters
    ----------
    input_file : str
        Path to the raw input CSV.
    output_file : str
        Path to save the processed CSV.
    config : ProcessorConfig, optional
        Processing configuration (target, outlier policy, etc.).

    Returns
    -------
    pd.DataFrame
        Cleaned and processed dataset.
    """

    # Load raw dataset
    df = load_csv(input_file)
    logger.info("Loaded shape: %s", df.shape)

    # Ensure required target column exists
    require_columns(df, [config.target])

    # Impute missing values
    df = fill_missing(df)

    # Apply outlier policy (filter/clip/none)
    df = apply_outlier_policy(
        df,
        column=config.target,
        policy=config.outlier_policy,
        k=config.iqr_multiplier,
    )

    # Save processed dataset
    save_csv(df, output_file, index=config.save_index)
    logger.info("Saved processed data to %s (shape=%s)", output_file, df.shape)

    return df


# -------------------------------------------------------------------
# Script entry point
# -------------------------------------------------------------------

if __name__ == "__main__":
    # Minimal local run for quick testing
    process_data("data/raw/house_data.csv", "data/processed/cleaned_house_data.csv")
