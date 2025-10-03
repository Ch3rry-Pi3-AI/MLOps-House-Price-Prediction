# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------
from __future__ import annotations

import logging
import platform
from pathlib import Path
from typing import Optional

import joblib
import mlflow
import mlflow.sklearn  # required for mlflow.sklearn.log_model
import numpy as np
import pandas as pd
import sklearn
import xgboost as xgb
from mlflow.models import infer_signature
from mlflow.tracking import MlflowClient
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from .builders import get_model_instance
from .config import TrainingConfig, load_training_config


# -------------------------------------------------------------------
# Logger
# -------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("training-pipeline")


# -------------------------------------------------------------------
# Orchestrator
# -------------------------------------------------------------------

def run_training(
    config_path: str | Path,
    data_path: str | Path,
    models_dir: str | Path,
    mlflow_tracking_uri: Optional[str] = None,
) -> None:
    """
    Train the final model and register it in MLflow, mirroring the original
    script's logic one-for-one.
    """
    # Load config
    cfg: TrainingConfig = load_training_config(config_path)
    model_cfg = cfg.model

    if mlflow_tracking_uri:
        mlflow.set_tracking_uri(mlflow_tracking_uri)
        mlflow.set_experiment(model_cfg.name)

    # Load data
    data = pd.read_csv(data_path)
    target = model_cfg.target_variable

    # Features & target
    X = data.drop(columns=[target])
    y = data[target]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Build model
    model = get_model_instance(model_cfg.best_model, model_cfg.parameters)

    # Start MLflow run
    with mlflow.start_run(run_name="final_training"):
        logger.info(f"Training model: {model_cfg.best_model}")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        mae = float(mean_absolute_error(y_test, y_pred))
        r2 = float(r2_score(y_test, y_pred))

        # Infer signature and provide a small input example
        input_example = X_train.head(2)
        signature = infer_signature(X_train, y_pred)

        # Log params & metrics
        mlflow.log_params(model_cfg.parameters)
        mlflow.log_metrics({"mae": mae, "r2": r2})

        # Explicit pip requirements to avoid "pip version" warning
        pip_requirements = [
            f"scikit-learn=={sklearn.__version__}",
            f"xgboost=={xgb.__version__}",
            f"pandas=={pd.__version__}",
            f"numpy=={np.__version__}",
            "cloudpickle",  # used by MLflow's sklearn flavor
            "mlflow",
        ]

        # Log model artifact using `name=` (non-deprecated)
        mlflow.sklearn.log_model(
            sk_model=model,
            name="tuned_model",
            signature=signature,
            input_example=input_example,
            pip_requirements=pip_requirements,
        )

        # Prepare registry details
        model_name = model_cfg.name
        run_id = mlflow.active_run().info.run_id
        # With `name="tuned_model"`, the artifact is at 'tuned_model' under the run
        model_uri = f"runs:/{run_id}/tuned_model"

        logger.info("Registering model to MLflow Model Registry...")
        client = MlflowClient()
        try:
            client.create_registered_model(model_name)
        except mlflow.exceptions.RestException:
            pass  # already exists

        model_version = client.create_model_version(
            name=model_name,
            source=model_uri,
            run_id=run_id,
        )

        # Use aliases (preferred over deprecated stages)
        client.set_registered_model_alias(
            name=model_name,
            alias="staging",
            version=model_version.version,
        )

        # Human-readable description
        description = (
            f"Model for predicting house prices.\n"
            f"Algorithm: {model_cfg.best_model}\n"
            f"Hyperparameters: {model_cfg.parameters}\n"
            f"Features used: All features in the dataset except the target variable\n"
            f"Target variable: {target}\n"
            f"Trained on dataset: {data_path}\n"
            f"Model saved at: {models_dir}/trained/{model_name}.pkl\n"
            f"Performance metrics:\n"
            f"  - MAE: {mae:.2f}\n"
            f"  - R²: {r2:.4f}"
        )
        client.update_registered_model(name=model_name, description=description)

        # Tags for organization
        client.set_registered_model_tag(model_name, "algorithm", model_cfg.best_model)
        client.set_registered_model_tag(model_name, "hyperparameters", str(model_cfg.parameters))
        client.set_registered_model_tag(model_name, "features", "All features except target variable")
        client.set_registered_model_tag(model_name, "target_variable", target)
        client.set_registered_model_tag(model_name, "training_dataset", str(data_path))
        client.set_registered_model_tag(
            model_name, "model_path", f"{models_dir}/trained/{model_name}.pkl"
        )

        # Dependency/version tags
        deps = {
            "python_version": platform.python_version(),
            "scikit_learn_version": sklearn.__version__,
            "xgboost_version": xgb.__version__,
            "pandas_version": pd.__version__,
            "numpy_version": np.__version__,
        }
        for k, v in deps.items():
            client.set_registered_model_tag(model_name, k, v)

        # Save model locally (ensure directory exists first)
        save_path = Path(models_dir) / "trained" / f"{model_name}.pkl"
        save_path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump(model, save_path)
        logger.info(f"Saved trained model to: {save_path}")
        logger.info(f"Final MAE: {mae:.2f}, R²: {r2:.4f}")
