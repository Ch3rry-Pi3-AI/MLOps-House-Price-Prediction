# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------
from __future__ import annotations

import argparse

from .processor import run_training

# -------------------------------------------------------------------
# CLI
# -------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Train and register final model from config.")
    p.add_argument("--config", type=str, required=True, help="Path to model_config.yaml")
    p.add_argument("--data", type=str, required=True, help="Path to processed CSV dataset")
    p.add_argument("--models-dir", type=str, required=True, help="Directory to save trained model")
    p.add_argument("--mlflow-tracking-uri", type=str, default=None, help="MLflow tracking URI")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    run_training(
        config_path=args.config,
        data_path=args.data,
        models_dir=args.models_dir,
        mlflow_tracking_uri=args.mlflow_tracking_uri,
    )


if __name__ == "__main__":
    main()
