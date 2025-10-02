# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

import logging
from pathlib import Path
import pandas as pd


# -------------------------------------------------------------------
# Logger setup
# -------------------------------------------------------------------

logger = logging.getLogger("data-io")


# -------------------------------------------------------------------
# CSV I/O helpers
# -------------------------------------------------------------------

def load_csv(path: str | Path) -> pd.DataFrame:
    """
    Load a CSV file into a DataFrame.

    Parameters
    ----------
    path : str or pathlib.Path
        Path to the CSV file.

    Returns
    -------
    pd.DataFrame
        Loaded dataset.
    """

    path = Path(path)
    logger.info("Loading CSV: %s", path)
    return pd.read_csv(path)


def save_csv(df: pd.DataFrame, path: str | Path, index: bool = False) -> None:
    """
    Save a DataFrame to a CSV file.

    Parameters
    ----------
    df : pd.DataFrame
        Data to save.
    path : str or pathlib.Path
        Destination file path.
    index : bool, default=False
        Whether to include the DataFrame index in the output.
    """

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)  # Ensure directories exist
    logger.info("Saving CSV: %s (index=%s)", path, index)
    df.to_csv(path, index=index)
