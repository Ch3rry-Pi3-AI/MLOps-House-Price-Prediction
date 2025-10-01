# **Data Preprocessing Stage**

This branch extends the **MLOps House Price Prediction** project by implementing the **data preprocessing pipeline**.
It introduces a modular structure under `src/data/` for loading, cleaning, and handling outliers, alongside a full test suite and automation via `invoke`.

The pipeline can now take raw data (`data/raw/`) and output cleaned data (`data/processed/cleaned_house_data.csv`) with missing value imputation and configurable outlier handling.



## **Project Structure**

```
mlops-house-price-prediction/
├── .venv/
├── data/
│   ├── raw/
│   └── processed/
│       └── cleaned_house_data.csv  # 🚀 NEW: Example processed dataset
├── deployment/
│   ├── kubernetes/
│   └── mlflow/
├── models/
│   └── trained/
├── notebooks/
├── src/
│   ├── api/
│   ├── data/                       # 🚀 NEW: Preprocessing modules
│   │   ├── cleaning.py             # 🚀 NEW: Missing value handling
│   │   ├── config.py               # 🚀 NEW: Config (dataclass, YAML loader)
│   │   ├── io.py                   # 🚀 NEW: CSV/Parquet load & save helpers
│   │   ├── outliers.py             # 🚀 NEW: Outlier detection & policies
│   │   ├── processor.py            # 🚀 NEW: Orchestrator for preprocessing
│   │   ├── schema.py               # 🚀 NEW: Schema/column validation
│   │   └── cli.py                  # 🚀 NEW: Command-line entrypoint for preprocessing
│   ├── features/
│   └── models/
├── streamlit_app/
├── tests/                          # 🚀 NEW: Test suite
│   ├── conftest.py                 # 🚀 NEW: Shared fixtures + sys.path shim
│   └── data/
│       ├── test_cleaning.py        # 🚀 NEW: Unit tests for cleaning
│       ├── test_io.py              # 🚀 NEW: Unit tests for IO
│       ├── test_outliers.py        # 🚀 NEW: Unit tests for outliers
│       ├── test_processor_integration.py # 🚀 NEW: End-to-end integration test
│       └── test_schema.py          # 🚀 NEW: Unit tests for schema checks
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
├── requirements.txt
├── tasks.py                        # 🚀 NEW: Invoke task runner (tests, lint, preprocess, serve, etc.)
└── uv.lock
```

> Note: Any `.venv/` folder is ignored and should not be committed.



## **Development Environment**

This project uses [uv](https://github.com/astral-sh/uv) for Python environment and dependency management.
You will also need Docker for running MLflow locally and Kubernetes manifests for deployment.

### 1) Prerequisites

Install the following tools:

* [Python 3.13](https://www.python.org/downloads/)
* [Git](https://git-scm.com/)
* [Visual Studio Code](https://code.visualstudio.com/) (or another editor)
* [uv – Python package and environment manager](https://github.com/astral-sh/uv)
* [Docker Desktop](https://www.docker.com/products/docker-desktop)

### 2) Clone the repository

```bash
git clone https://github.com/<your-username>/MLOps-House-Price-Prediction.git
cd MLOps-House-Price-Prediction
```

### 3) Create a virtual environment

```bash
uv venv --python python3.13
```

Activate it:

```bash
# On Linux / macOS
source .venv/bin/activate

# On Windows (PowerShell)
.venv\Scripts\Activate.ps1

# On Windows (Git Bash)
source .venv/Scripts/activate
```

### 4) Install dependencies

```bash
uv pip install -r requirements.txt
```

### 5) Deactivate when done

```bash
deactivate
```



## **Running Preprocessing**

You can now run the preprocessing pipeline in two ways:

### 1. Direct Python Execution

```bash
python -m src.data.processor
```

This will load the raw dataset from `data/raw/house_data.csv` and write the cleaned version to `data/processed/cleaned_house_data.csv`.



### 2. Using Invoke Tasks

The project includes an `invoke`-based task runner (`tasks.py`) with common commands:

```bash
# run tests
invoke test

# run a subset
invoke test -k cleaning

# run with coverage
invoke cov

# optional: if you install black/ruff
invoke fmt
invoke lint

# clean caches
invoke clean

# Preprocess with defaults
invoke preprocess

# Preprocess with clipping and a different target
invoke preprocess --policy=clip --target=SalePrice --iqr=2.0

# Create common dirs
invoke ensure-dirs
```



✅ With this stage complete, the project now has a fully modular preprocessing pipeline, automated testing, and developer productivity commands via Invoke. This ensures data consistency and makes the foundation ready for **feature engineering** and **model training** in the next stage.

