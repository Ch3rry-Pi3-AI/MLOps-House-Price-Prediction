# **Feature Engineering Stage**

This branch extends the **MLOps House Price Prediction** project by implementing the **feature engineering pipeline**.
It introduces a modular structure under `src/features/` for engineered columns and a reusable scikit-learn **preprocessor** (saved as a `.pkl` in `models/trained/`), a full test suite under `tests/features/`, and updated automation via `invoke`.

A new notebook support the **data scientist → ML engineer** workflow:

* `notebooks/03_feature_engineering.ipynb` – interactive development of feature logic prior to modularisation.

The pipeline consumes the **cleaned data** produced by the preprocessing stage and outputs **engineered features** plus a **pickled preprocessor** for downstream model training.



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
│       └── engineered_features.csv         # 🚀 NEW: output from feature engineering (example)
├── deployment/
│   ├── kubernetes/
│   └── mlflow/
├── models/
│   └── trained/
│       └── preprocessor.pkl                # 🚀 NEW: fitted ColumnTransformer (pickle)
├── notebooks/
│   ├── 01_data_preprocessing.ipynb
│   ├── 02_eda.ipynb                        
│   └── 03_feature_engineering.ipynb        # 🚀 NEW: Feature engineering notebook
├── src/
│   ├── api/
│   ├── data/                               
│   │   ├── cleaning.py
│   │   ├── config.py
│   │   ├── io.py
│   │   ├── outliers.py
│   │   ├── processor.py
│   │   ├── schema.py
│   │   └── cli.py
│   ├── features/                           # 🚀 NEW: Feature engineering modules
│   │   ├── builders.py                     #   Feature creation + preprocessor definition
│   │   ├── processor.py                    #   Orchestrator (fit/transform + persist)
│   │   ├── config.py                       #   FeaturesConfig dataclass + YAML loader
│   │   └── cli.py                          #   Command-line entrypoint (flags + YAML)
│   └── models/
├── streamlit_app/
├── tests/
│   ├── conftest.py
│   ├── data/                               
│   └── features/                           # 🚀 NEW: Feature engineering tests
│       ├── conftest.py
│       ├── test_builders_features.py
│       ├── test_builders_preprocessor.py
│       ├── test_processor_integration.py
│       └── test_cli.py
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
├── requirements.txt
├── tasks.py                                # ✅ Updated: includes features tasks
└── uv.lock
```

> Note: Any `.venv/` folder is ignored and should not be committed.

## **Module Overview (with build order)**

### 1) `src/features/builders.py` – Feature & Preprocessor Builders

* `create_features(df)`: adds `house_age`, `price_per_sqft`, `bed_bath_ratio` (with safe division).
* `create_preprocessor()`: returns a `ColumnTransformer` with numeric imputation and categorical one-hot encoding.

### 2) `src/features/processor.py` – Orchestrator

* Loads cleaned CSV → applies `create_features` → fits and transforms via `create_preprocessor`.
* Saves transformed dataset to CSV and the **fitted preprocessor** to `models/trained/preprocessor.pkl` (pickle).

### 3) `src/features/config.py` – Configuration

* `FeaturesConfig` (frozen dataclass) with `input`, `output`, `preprocessor`.
* `load_features_config(path)` to load YAML (e.g., `engineer.yaml`).

### 4) `src/features/cli.py` – CLI Entrypoint

* Flags: `--input`, `--output`, `--preprocessor`, `--config`.
* **Precedence:** load defaults from YAML (if provided), then override with flags; if still unset, `preprocessor` defaults to `models/trained/preprocessor.pkl`.

## **Development Environment**

Same environment as the preprocessing stage (Python, `uv`, etc.). If you haven’t already:

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

## **Running Feature Engineering**

You can run this stage in several ways.

### 1) Notebook Execution (Data Scientist Workflow)

* Explore cleaned data in `notebooks/02_eda.ipynb`.
* Prototype features in `notebooks/03_feature_engineering.ipynb`.
  Once validated, promote the logic into `src/features/` and rely on CI/tests.

### 2) Direct Python Execution (ML Engineer Workflow)

```bash
python -m src.features.processor
```

Runs with defaults:
`data/processed/cleaned_house_data.csv` → `data/processed/engineered_features.csv`
and saves `models/trained/preprocessor.pkl`.

### 3) Command-Line Interface (CLI)

**Explicit flags**

```bash
python -m src.features.cli \
  --input data/processed/cleaned_house_data.csv \
  --output data/processed/engineered_features.csv \
  --preprocessor models/trained/preprocessor.pkl
```

**YAML config** (`engineer.yaml`)

```yaml
# engineer.yaml
input: data/processed/cleaned_house_data.csv
output: data/processed/engineered_features.csv
preprocessor: models/trained/preprocessor.pkl
```

Run with YAML:

```bash
python -m src.features.cli --config=engineer.yaml
```

> **Note:** CLI flags override YAML values when both are provided.

### 4) Invoke Task Runner

```bash
# run only feature engineering tests
invoke features-test

# run feature pipeline only
invoke engineer

# run tests first, then the feature pipeline (recommended)
invoke features

# run feature pipeline with custom paths
invoke features --input=data/processed/cleaned_house_data.csv \
                --output=data/processed/engineered_features.csv \
                --preprocessor=models/trained/preprocessor.pkl
```

> You can also still run the general test suite and coverage:
>
> ```bash
> invoke test
> invoke cov
> ```

## **Testing**

The suite under `tests/features/` provides both unit and integration coverage:

* **Unit:** `test_builders_features.py`, `test_builders_preprocessor.py`
* **Integration:** `test_processor_integration.py` (checks CSV + pickle artefacts)
* **CLI:** `test_cli.py` (smoke test for `src.features.cli`)

Run all tests:

```bash
pytest -q
```

Run only feature engineering tests:

```bash
pytest tests/features -v
```

## **Continuous Integration (CI/CD)**

Your existing GitHub Actions workflow (`.github/workflows/ci.yml`) automatically runs `pytest` on every push/PR.
It will now include the **feature engineering** tests alongside preprocessing.
Add code, push, and CI will tell you whether everything still passes ✅.

## ✅ Summary

With this stage, the project now has:

* A **feature engineering** pipeline (`src/features/`) producing engineered datasets and a **reusable preprocessor** (`models/trained/preprocessor.pkl`).
* Two supporting notebooks: **EDA** (`02_eda.ipynb`) and **Feature Engineering** (`03_feature_engineering.ipynb`).
* A dedicated **test suite** for this stage (`tests/features/`).
* Updated **Invoke** tasks for fast, reproducible workflows.
* Seamless integration with existing **CI** to keep the branch green.

This clearly separates the **exploration** (notebooks) from the **engineering** (modules + tests + CI), paving the way for the next stage: **model training**.