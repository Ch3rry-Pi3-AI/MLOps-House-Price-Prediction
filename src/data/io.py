import logging
from pathlib import Path
import pandas as pd

logger = logging.getLogger("data-io")


def load_csv(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    logger.info("Loading CSV: %s", path)
    return pd.read_csv(path)


def save_csv(df: pd.DataFrame, path: str | Path, index: bool = False) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    logger.info("Saving CSV: %s (index=%s)", path, index)
    df.to_csv(path, index=index)
