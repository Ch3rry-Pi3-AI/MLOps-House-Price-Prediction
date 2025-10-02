# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

from dataclasses import dataclass
from typing import Literal, Optional
import yaml  # Only used in optional YAML loader


# -------------------------------------------------------------------
# Type aliases
# -------------------------------------------------------------------

OutlierPolicy = Literal["filter", "clip", "none"]


# -------------------------------------------------------------------
# Configuration dataclass
# -------------------------------------------------------------------

@dataclass(frozen=True)
class ProcessorConfig:
    """
    Configuration for data preprocessing.

    Parameters
    ----------
    target : str, default="price"
        Name of the target variable to predict.
    outlier_policy : {"filter", "clip", "none"}, default="filter"
        Strategy for handling outliers:
        - "filter": Remove outliers beyond IQR whiskers.
        - "clip": Cap values at IQR whisker boundaries.
        - "none": Leave data unchanged.
    iqr_multiplier : float, default=1.5
        Whisker width multiplier for IQR outlier detection.
    save_index : bool, default=False
        Whether to include the index when saving to CSV.
    """

    target: str = "price"
    outlier_policy: OutlierPolicy = "filter"
    iqr_multiplier: float = 1.5
    save_index: bool = False


# -------------------------------------------------------------------
# YAML loader
# -------------------------------------------------------------------

def load_yaml_config(path: str) -> ProcessorConfig:
    """
    Load configuration parameters from a YAML file.

    Parameters
    ----------
    path : str
        Path to the YAML configuration file.

    Returns
    -------
    ProcessorConfig
        Populated configuration object.
    """

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}

    return ProcessorConfig(**data)
