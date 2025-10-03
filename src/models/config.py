# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any
import yaml


# -------------------------------------------------------------------
# Dataclasses mirroring YAML structure
# -------------------------------------------------------------------

@dataclass(frozen=True)
class ModelSection:
    """Model section inside the training YAML.

    Parameters
    ----------
    name : str
        Registered model name / experiment name.
    best_model : str
        Chosen algorithm identifier (e.g., "RandomForest").
    parameters : dict
        Hyperparameters to instantiate the model with.
    target_variable : str
        Name of the target column in the dataset.
    """

    name: str
    best_model: str
    parameters: Dict[str, Any]
    target_variable: str


@dataclass(frozen=True)
class TrainingConfig:
    """Top-level training configuration.

    Attributes
    ----------
    model : ModelSection
        The model-related configuration block.
    """

    model: ModelSection


# -------------------------------------------------------------------
# YAML loader
# -------------------------------------------------------------------

def load_training_config(path: str | Path) -> TrainingConfig:
    """Load the training config YAML into a dataclass."""
    with open(path, "r") as f:
        raw = yaml.safe_load(f)
    model_raw = raw["model"]
    model = ModelSection(
        name=model_raw["name"],
        best_model=model_raw["best_model"],
        parameters=model_raw.get("parameters", {}),
        target_variable=model_raw["target_variable"],
    )
    return TrainingConfig(model=model)