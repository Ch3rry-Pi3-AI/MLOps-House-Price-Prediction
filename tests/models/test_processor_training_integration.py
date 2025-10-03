# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------
from pathlib import Path
import pandas as pd
import mlflow
from mlflow.tracking import MlflowClient

from src.models.processor import run_training


# -------------------------------------------------------------------
# Helpers
# -------------------------------------------------------------------

def _file_uri(p: Path) -> str:
    # Windows-safe file URI (e.g., file:///C:/...) and works on POSIX too
    return p.resolve().as_uri()


# -------------------------------------------------------------------
# Integration test
# -------------------------------------------------------------------

def test_end_to_end_training_with_local_registry(tmp_path: Path, df_features_minimal: pd.DataFrame):
    # Prepare tiny dataset with a target column 'price'
    data_csv = tmp_path / "engineered.csv"
    df_features_minimal.to_csv(data_csv, index=False)

    # Minimal training config YAML
    cfg = tmp_path / "model_config.yaml"
    cfg.write_text(
        """
model:
  name: house_price_model
  best_model: GradientBoosting
  parameters:
    n_estimators: 20
    learning_rate: 0.1
    max_depth: 3
  target_variable: price
"""
    )

    models_dir = tmp_path / "models"
    tracking_dir = tmp_path / "mlruns"
    tracking_uri = _file_uri(tracking_dir)

    # Run training
    run_training(
        config_path=str(cfg),
        data_path=str(data_csv),
        models_dir=str(models_dir),
        mlflow_tracking_uri=tracking_uri,
    )

    # Local .pkl should exist
    expected_pkl = models_dir / "trained" / "house_price_model.pkl"
    assert expected_pkl.exists(), "Trained model pickle should be written."

    # Verify model is registered and alias exists (file-backed registry)
    mlflow.set_tracking_uri(tracking_uri)
    client = MlflowClient()
    rm = client.get_registered_model("house_price_model")
    assert rm.name == "house_price_model"

    # Check at least one version exists and carries alias 'staging' (newer MLflow)
    versions = client.search_model_versions("name='house_price_model'")
    assert any(getattr(v, "aliases", []) and "staging" in v.aliases for v in versions), \
        "Expected alias 'staging' on at least one model version."