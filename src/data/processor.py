import logging
from pathlib import Path
import pandas as pd

from .config import ProcessorConfig
from .io import load_csv, save_csv
from .schema import require_columns
from .cleaning import fill_missing
from .outliers import apply_outlier_policy

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("data-processor")


def process_data(
    input_file: str, output_file: str, config: ProcessorConfig = ProcessorConfig()
) -> pd.DataFrame:
    df = load_csv(input_file)
    logger.info("Loaded shape: %s", df.shape)

    require_columns(df, [config.target])
    df = fill_missing(df)
    df = apply_outlier_policy(
        df, column=config.target, policy=config.outlier_policy, k=config.iqr_multiplier
    )

    save_csv(df, output_file, index=config.save_index)
    logger.info("Saved processed data to %s (shape=%s)", output_file, df.shape)
    return df


if __name__ == "__main__":
    # Minimal local run
    process_data("data/raw/house_data.csv", "data/processed/cleaned_house_data.csv")
