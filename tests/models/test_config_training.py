# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------
from pathlib import Path

from src.models.config import load_training_config, TrainingConfig


# -------------------------------------------------------------------
# Tests: config loader
# -------------------------------------------------------------------

def test_load_training_config_roundtrip(tmp_path: Path):
    cfg_path = tmp_path / "model_config.yaml"
    cfg_path.write_text(
        """
model:
  name: house_price_model
  best_model: GradientBoosting
  parameters:
    n_estimators: 50
    learning_rate: 0.1
    max_depth: 3
  target_variable: price
"""
    )

    cfg: TrainingConfig = load_training_config(cfg_path)
    assert cfg.model.name == "house_price_model"
    assert cfg.model.best_model == "GradientBoosting"
    assert cfg.model.parameters["n_estimators"] == 50
    assert cfg.model.target_variable == "price"