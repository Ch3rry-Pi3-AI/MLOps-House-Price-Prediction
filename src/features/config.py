# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

from dataclasses import dataclass
import yaml
from pathlib import Path


# -------------------------------------------------------------------
# Config dataclass
# -------------------------------------------------------------------

@dataclass(frozen=True)
class FeaturesConfig:
    """
    Configuration for feature engineering.

    Parameters
    ----------
    input : str
        Path to the cleaned CSV file.
    output : str
        Path for engineered CSV output.
    preprocessor : str
        Path for saving fitted preprocessor (pickle).
    """

    input: str = "data/processed/cleaned_house_data.csv"
    output: str = "data/processed/engineered_features.csv"
    preprocessor: str = "models/trained/preprocessor.pkl"


# -------------------------------------------------------------------
# YAML loader
# -------------------------------------------------------------------

def load_features_config(path: str | Path) -> FeaturesConfig:
    """
    Load a FeaturesConfig from YAML.
    """
    with open(path, "r") as f:
        data = yaml.safe_load(f)
    return FeaturesConfig(**data)
