# **Model Training Modules — House Price Prediction (Inference Pipeline Stage)**

This folder contains the **model training pipeline** for the **MLOps House Price Prediction** project.
It extends the engineered dataset from the **feature engineering stage** by fitting and evaluating final models, logging all results to **MLflow**, and registering the trained model (both locally and in the MLflow Model Registry).

Before training, ensure that the **MLflow tracking server** (defined under `deployment/mlflow/`) is up and running — this container is required for experiment tracking and model registration.



## **Design Overview**

The module follows **single-responsibility principles**, ensuring a clean separation between model construction, orchestration, configuration, and command-line execution:

* `builders.py` → model instantiation logic
* `processor.py` → training orchestration, evaluation, persistence, and MLflow integration
* `config.py` → configuration dataclass and YAML loader
* `cli.py` → command-line access for reproducible training

This structure provides a **modular, testable, and production-ready workflow** that integrates seamlessly with MLflow.



## **Module Structure**

```
src/models/
├── builders.py       # Model factory (maps model names → estimators)
├── processor.py      # Orchestrator for training, evaluation, MLflow logging
├── config.py         # TrainingConfig dataclass + YAML loader
├── cli.py            # Command-line entrypoint
```

## **MLflow Container Dependency**

To use MLflow tracking and model registry features, the **MLflow container must be running** before you start training.

The **Docker Compose file** for MLflow is located at:

```
deployment/mlflow/docker-compose.yaml
```

### 🧩 Example docker-compose.yaml (for reference)

```yaml
version: "3.9"
services:
  mlflow:
    build: .
    ports:
      - "5555:5000"
    environment:
      MLFLOW_TRACKING_URI: http://0.0.0.0:5000
    volumes:
      - ./mlflow_data:/mlflow
      - ./mlartifacts:/mlartifacts
```



### ⚙️ Running MLflow via Docker Compose

From the project root:

```bash
cd deployment/mlflow
docker compose up -d
```

You can check that it’s running:

```bash
docker ps
```

You should see a container exposing port `5555 → 5000`.

Then, open:

👉 [http://localhost:5555](http://localhost:5555)

That’s your live **MLflow Tracking UI**.
Once it’s confirmed running, proceed with model training.



## **Module Overview (Build Order)**

If setting up this folder **from scratch**, the natural build and dependency order is as follows:



### 1️⃣ `builders.py` — Model Builders

**Purpose**

* Provides a `get_model_instance(name, params)` function that returns a configured estimator object.
* Supports scikit-learn and XGBoost estimators such as `LinearRegression`, `RandomForestRegressor`, `GradientBoostingRegressor`, and `XGBRegressor`.

**Dependencies:**
`scikit-learn`, `xgboost`

**Why first:**
Defines the reusable model factory used by all other modules.



### 2️⃣ `processor.py` — Orchestrator

**Purpose**

* Loads the YAML configuration (`TrainingConfig`)
* Reads engineered dataset (`data/processed/engineered_features.csv`)
* Trains the selected model via `builders.get_model_instance()`
* Evaluates using metrics like MAE, R²
* Logs parameters, metrics, and model artifacts to **MLflow**
* Registers the model in the MLflow Model Registry (`@staging` alias)
* Saves the trained model locally under `models/trained/{model_name}.pkl`

**Dependencies:**
`pandas`, `numpy`, `scikit-learn`, `xgboost`, `mlflow`, `joblib`, `logging`

**Why second:**
Coordinates the full training, evaluation, and logging pipeline.



### 3️⃣ `config.py` — Configuration

**Purpose**

* Defines `TrainingConfig` and `ModelSection` dataclasses
* Provides `load_training_config(path)` to parse YAML files
* Centralises configuration of hyperparameters, dataset paths, and target variables

**Why third:**
Ensures a consistent and flexible configuration interface across environments.



### 4️⃣ `cli.py` — Command-Line Entrypoint

**Purpose**

* Provides a CLI wrapper for the training pipeline
* Enables reproducible execution with argument flags

**Features**

| Flag                    | Description                           |
| -- | - |
| `--config`              | Path to training config YAML          |
| `--data`                | Path to processed dataset             |
| `--models-dir`          | Directory to save trained model       |
| `--mlflow-tracking-uri` | URI of running MLflow tracking server |

**Why last:**
Provides the user-facing interface to the training workflow.



## **Execution**

### 🧪 Option 1 — Direct Python Execution

Runs the training process with parameters from the YAML config.

```bash
python -m src.models.processor
```

Example YAML config path:
`configs/model_config.yaml`



### ⚙️ Option 2 — Command-Line Interface

Run with explicit arguments:

```bash
python -m src.models.cli \
  --config configs/model_config.yaml \
  --data data/processed/engineered_features.csv \
  --models-dir models \
  --mlflow-tracking-uri http://localhost:5555
```



**Example `model_config.yaml`:**

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



### 🧰 Option 3 — Invoke Task Runner

Run the full training pipeline:

```bash
invoke train
```

Run pipeline only (skip tests):

```bash
invoke train-only
```

Run with custom arguments:

```bash
invoke train \
  --config=configs/model_config.yaml \
  --data=data/processed/engineered_features.csv \
  --models-dir=models \
  --mlflow-tracking-uri=http://localhost:5555
```



## **Verification: Check MLflow Tracking**

After training completes, open your MLflow UI at
👉 [http://localhost:5555](http://localhost:5555)

You should see:

* A new **experiment run** with metrics (MAE, R²)
* Logged parameters and model artifacts
* A **registered model version** with alias `@staging`



## ✅ **Summary**

This folder implements a **robust, modular model training stage** that integrates seamlessly with the MLflow container.

| Component                               | Purpose                                          |
|  |  |
| `builders.py`                           | Defines supported estimator types                |
| `processor.py`                          | Orchestrates training, evaluation, and logging   |
| `config.py`                             | Manages hyperparameter and dataset configuration |
| `cli.py`                                | Provides CLI for reproducible training           |
| `deployment/mlflow/docker-compose.yaml` | Runs the MLflow tracking server                  |

### 🚀 Produces:

* Trained model artifact in `models/trained/`
* Logged run in MLflow UI (`http://localhost:5555`)
* Registered model version (`@staging`)

> ✅ **Reminder:** Before running training, start the MLflow container:
>
> ```bash
> cd deployment/mlflow
> docker compose up -d
> ```
>
> Then verify it’s running with:
>
> ```bash
> docker ps
> ```
>
> and proceed to train your model.

This ensures all runs, metrics, and models are correctly tracked and versioned within MLflow — completing the **Model Training → Inference** workflow.