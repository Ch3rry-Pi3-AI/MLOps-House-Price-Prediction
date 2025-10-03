# **Model Training Stage**

This branch extends the **MLOps House Price Prediction** project by implementing the **model training pipeline**.
It introduces a modular structure under `src/models/` for estimator creation, orchestration, and CLI, a full test suite under `tests/models/`, and updated automation via `invoke`.

A new notebook supports the **data scientist → ML engineer** workflow:

* `notebooks/04_model_training.ipynb` – interactive development of training and MLflow logging prior to modularisation.

The pipeline consumes the **engineered features** produced by the feature engineering stage and outputs a **trained model** (`.pkl`), fully logged and registered in **MLflow** with metrics, parameters, tags, and versioning.



## **Project Structure**

```
mlops-house-price-prediction/
├── .venv/
├── .github/
│   └── workflows/
│       └── ci.yml
├── data/
│   ├── raw/
│   └── processed/
│       ├── cleaned_house_data.csv
│       ├── engineered_features.csv
├── deployment/
│   ├── kubernetes/
│   └── mlflow/
├── models/
│   └── trained/
│       ├── preprocessor.pkl
│       └── house_price_model.pkl         # 🚀 NEW: trained regression model (pickle)
├── notebooks/
│   ├── 01_data_preprocessing.ipynb
│   ├── 02_eda.ipynb
│   ├── 03_feature_engineering.ipynb
│   └── 04_model_training.ipynb           # 🚀 NEW: Model training notebook
├── src/
│   ├── api/
│   ├── data/
│   ├── features/
│   └── models/                           # 🚀 NEW: Model training modules
│       ├── builders.py                   #   Estimator factory (sklearn/xgboost)
│       ├── processor.py                  #   Orchestrator (train + MLflow + persist)
│       ├── config.py                     #   TrainingConfig dataclass + YAML loader
│       └── cli.py                        #   Command-line entrypoint
├── streamlit_app/
├── tests/
│   ├── conftest.py
│   ├── data/
│   ├── features/
│   └── models/                           # 🚀 NEW: Model training tests
│       ├── conftest.py                   #   Fixtures (synthetic df with target `price`)
│       ├── test_builders_models.py       #   Tests for estimator factory
│       ├── test_config_training.py       #   Tests for config loading
│       ├── test_processor_training_integration.py  #   End-to-end training + MLflow
│       └── test_cli_models.py            #   CLI smoke test
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
├── requirements.txt
├── tasks.py                              # ✅ Updated: includes model tasks
└── uv.lock
```

> Note: Any `.venv/` folder is ignored and should not be committed.



## **Module Overview (with build order)**

### 1) `src/models/builders.py` – Model Builders

* `get_model_instance(name, params)`: returns a scikit-learn or XGBoost estimator.
* Supports: `LinearRegression`, `RandomForestRegressor`, `GradientBoostingRegressor`, `XGBRegressor`.
* Raises `ValueError` for unsupported names.



### 2) `src/models/processor.py` – Orchestrator

* Loads engineered dataset and target.
* Splits train/test.
* Trains the configured model.
* Logs parameters, metrics, model artifact, and environment to **MLflow**.
* Registers model with alias `@staging`.
* Saves the trained `.pkl` to `models/trained/`.



### 3) `src/models/config.py` – Configuration

* `TrainingConfig` dataclass, wrapping model name, parameters, and target.
* `load_training_config(path)` loads YAML into `TrainingConfig`.

Example config (`configs/model_config.yaml`):

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



### 4) `src/models/cli.py` – CLI Entrypoint

* Flags: `--config`, `--data`, `--models-dir`, `--mlflow-tracking-uri`.
* Runs training directly from the shell.
* Supports YAML-first configs, with CLI overrides.



## **Development Environment**

Same environment as earlier stages. If you haven’t already:

```bash
uv venv --python python3.13

# On Linux / macOS
source .venv/bin/activate

# On Windows (PowerShell)
.venv\Scripts\Activate.ps1

# On Windows (Git Bash)
source .venv/Scripts/activate

uv pip install -r requirements.txt
```

Ensure common directories exist:

```bash
invoke ensure-dirs
```



## **Running Model Training**

You can run this stage in several ways.

### 1) Notebook Execution (Data Scientist Workflow)

* Prototype training in `notebooks/04_model_training.ipynb`.
* Once validated, promote code into `src/models/` and rely on CLI + CI.



### 2) Direct Python Execution (ML Engineer Workflow)

```bash
python -m src.models.processor
```

Runs with defaults:
`configs/model_config.yaml` + `data/processed/engineered_features.csv`
→ trains and saves `models/trained/house_price_model.pkl`.



### 3) Command-Line Interface (CLI)

**Explicit flags**

```bash
python -m src.models.cli \
  --config configs/model_config.yaml \
  --data data/processed/engineered_features.csv \
  --models-dir models \
  --mlflow-tracking-uri http://localhost:5555
```



### 4) Invoke Task Runner

```bash
# run only model tests
invoke models-test

# run training pipeline only
invoke train

# run tests first, then the training pipeline (recommended)
invoke models

# run training pipeline with custom MLflow URI (Docker MLflow server)
invoke models --mlflow-tracking-uri=http://localhost:5555
```



## **Testing**

The suite under `tests/models/` provides both unit and integration coverage:

* **Unit:**

  * `test_builders_models.py` (estimator mapping)
  * `test_config_training.py` (YAML → dataclass)
* **Integration:**

  * `test_processor_training_integration.py` (end-to-end training, MLflow run + pickle output)
* **CLI:**

  * `test_cli_models.py` (smoke test for `src.models.cli`)

Run all tests:

```bash
pytest -q
```

Run only model-training tests:

```bash
pytest tests/models -v
```



## **Continuous Integration (CI/CD)**

Your GitHub Actions workflow (`.github/workflows/ci.yml`) automatically runs `pytest` on every push/PR.
It now includes the **model training** tests alongside preprocessing and feature engineering.
Add code, push, and CI will tell you whether everything still passes ✅.



## ✅ Summary

With this stage, the project now has:

* A **model training** pipeline (`src/models/`) producing a trained regression model.
* A supporting **notebook** for training (`04_model_training.ipynb`).
* A dedicated **test suite** for this stage (`tests/models/`).
* Updated **Invoke** tasks for reproducible workflows.
* Seamless integration with **MLflow** for experiment tracking and model registry.
* CI coverage for model training logic, ensuring robustness and reproducibility.

This clearly separates the **exploration** (notebooks) from the **engineering** (modules + tests + CI), paving the way for the next stage: **deployment**.