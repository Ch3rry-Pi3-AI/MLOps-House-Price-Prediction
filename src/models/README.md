# **Model Training Modules**

This folder contains the **model training pipeline** for the **MLOps House Price Prediction** project.
It extends the engineered dataset from the **feature engineering stage** by fitting a final model, logging results with **MLflow**, and registering the trained model (both locally and in the MLflow Model Registry).

The design again follows **single-responsibility principles**:

* `builders.py` → model instantiation logic
* `processor.py` → orchestration (training, evaluation, persistence, MLflow registry)
* `config.py` → configuration dataclass + YAML loader
* `cli.py` → command-line access

This ensures a modular, testable, and extensible workflow that can be run directly, via CLI/YAML, or integrated into deployment pipelines.



## **Module Structure**

```
src/models/
├── builders.py     # Model factory (map model names → estimators)
├── processor.py    # Orchestrator for training, MLflow logging, registry
├── config.py       # TrainingConfig dataclass + YAML loader
└── cli.py          # Command-line entrypoint
```



## **Module Overview (with build order)**

If building this folder **from scratch**, the natural order would be:

### 1. `builders.py` – Model Builders

* **Purpose**

  * `get_model_instance(name, params)`: return an estimator based on string key (`LinearRegression`, `RandomForest`, `GradientBoosting`, `XGBoost`).
* **Dependencies**: `scikit-learn`, `xgboost`.
* **Why first**: Core model construction logic used everywhere else.



### 2. `processor.py` – Orchestrator

* **Purpose**

  * Load training config (`config.yaml`)
  * Load engineered dataset (`data/processed/engineered_features.csv`)
  * Train the chosen model (`builders.get_model_instance`)
  * Evaluate with MAE and R²
  * Log parameters, metrics, and model with MLflow (including signature & input example)
  * Register model in the MLflow Model Registry and set alias `@staging`
  * Save trained model locally (`models/trained/{model_name}.pkl`)
* **Dependencies**: `pandas`, `numpy`, `scikit-learn`, `xgboost`, `mlflow`, `joblib`, `logging`.
* **Why second**: Orchestrates the full training and logging pipeline.



### 3. `config.py` – Configuration

* **Purpose**

  * `TrainingConfig` + `ModelSection` dataclasses to represent YAML config
  * `load_training_config(path)`: load YAML into `TrainingConfig`
* **Why third**: Centralises hyperparameters and dataset/target variable information.



### 4. `cli.py` – Command-Line Entrypoint

* **Purpose**: Wraps `processor.run_training` with `argparse`.
* **Features**:

  * Flags:

    * `--config` → path to model_config.yaml
    * `--data` → path to processed dataset
    * `--models-dir` → directory for trained model files
    * `--mlflow-tracking-uri` → MLflow server URI
* **Why last**: Provides a user-facing execution interface.



## **Execution**

### 1. Direct Python Execution

```bash
python -m src.models.processor
```

Runs with parameters from a YAML config (e.g. `configs/model_config.yaml`).



### 2. Command-Line Interface

Run with explicit flags:

```bash
python -m src.models.cli \
  --config configs/model_config.yaml \
  --data data/processed/engineered_features.csv \
  --models-dir models \
  --mlflow-tracking-uri http://localhost:5555
```

**Example `model_config.yaml`**

```yaml
model:
  name: house_price_model
  best_model: GradientBoosting
  parameters:
    n_estimators: 200
    learning_rate: 0.05
    max_depth: 3
  target_variable: price
```



### 3. Invoke Task Runner

Run training directly:

```bash
invoke train
```

Run pipeline only (skip tests):

```bash
invoke train-only
```

Run with custom flags:

```bash
invoke train --config=configs/model_config.yaml \
             --data=data/processed/engineered_features.csv \
             --models-dir=models \
             --mlflow-tracking-uri=http://localhost:5555
```



## ✅ Summary

This folder implements a **modular model training stage** with:

* `builders.py` → estimator instantiation
* `processor.py` → orchestration, evaluation, MLflow logging, registry
* `config.py` → centralised configuration with a YAML loader
* `cli.py` → simple CLI with flags + YAML support

The pipeline is **robust, testable, and production-ready**, producing:

* A logged MLflow run with metrics, parameters, model artifacts
* A registered model in the MLflow Model Registry with alias `@staging`
* A local `.pkl` copy of the trained model in `models/trained/`

