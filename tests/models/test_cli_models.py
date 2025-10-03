# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------
import sys
from pathlib import Path
import pandas as pd

from src.models import cli as models_cli


def _file_uri(p: Path) -> str:
    # Windows-safe file URI (e.g., file:///C:/...) and works on POSIX too
    return p.resolve().as_uri()


# -------------------------------------------------------------------
# CLI test
# -------------------------------------------------------------------

def test_cli_invocation_trains_and_saves(tmp_path, monkeypatch, df_features_minimal):
    # Inputs
    data_csv = tmp_path / "engineered.csv"
    df_features_minimal.to_csv(data_csv, index=False)

    cfg = tmp_path / "model_config.yaml"
    cfg.write_text(
        """
model:
  name: house_price_model
  best_model: GradientBoosting
  parameters:
    n_estimators: 10
    learning_rate: 0.1
    max_depth: 2
  target_variable: price
"""
    )

    models_dir = tmp_path / "models"
    tracking_uri = _file_uri(tmp_path / "mlruns")

    # Monkeypatch argv for argparse
    argv = [
        "python",
        "--config", str(cfg),
        "--data", str(data_csv),
        "--models-dir", str(models_dir),
        "--mlflow-tracking-uri", tracking_uri,
    ]
    monkeypatch.setattr(sys, "argv", argv)

    # Run CLI
    models_cli.main()

    # Outputs should exist
    expected_pkl = models_dir / "trained" / "house_price_model.pkl"
    assert expected_pkl.exists()