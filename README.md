# **Data Preprocessing Stage**

This branch extends the **MLOps House Price Prediction** project by implementing the **data preprocessing pipeline**.
It introduces a modular structure under `src/data/` for loading, cleaning, schema validation, and outlier handling, alongside a full test suite, automation via `invoke`, and GitHub Actions for CI/CD.

A new **data preprocessing notebook** (`notebooks/01_data_preprocessing.ipynb`) has also been added.
This represents the **data scientist's exploratory workflow**, where preprocessing logic is first developed interactively. Once validated, it is handed off to an **ML engineer**, who modularises the code under `src/data/` and integrates it into the CI/CD system.

The pipeline can now take raw data (`data/raw/`) and output cleaned data (`data/processed/cleaned_house_data.csv`) with missing value imputation and configurable outlier handling.

---

## **Project Structure**

```
mlops-house-price-prediction/
├── .venv/
├── .github/                        # 🚀 NEW: GitHub Actions configuration
│   └── workflows/
│       └── ci.yml                  # 🚀 NEW: CI pipeline (tests, linting, etc.)
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
│   └── 01_data_preprocessing.ipynb # 🚀 NEW: Data scientist's preprocessing notebook
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

---

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

---

## **Running Preprocessing**

You can now run the preprocessing pipeline in four ways:

### 1. Notebook Execution (Data Scientist Workflow)

Run and explore `notebooks/01_data_preprocessing.ipynb` interactively.
This is where preprocessing logic is first designed and validated.

### 2. Direct Python Execution (ML Engineer Workflow)

```bash
python -m src.data.processor
```

Runs the pipeline with defaults:
`data/raw/house_data.csv` → `data/processed/cleaned_house_data.csv`.

### 3. Command-Line Interface (CLI)

```bash
python -m src.data.cli --in data/raw/house_data.csv --out data/processed/cleaned_house_data.csv --policy filter
```

Supports YAML configs and runtime overrides.

### 4. Using Invoke Tasks

```bash
invoke preprocess
invoke preprocess --policy=clip --target=price --iqr=2.0
invoke test
invoke cov
```

---

## **Continuous Integration (CI/CD)**

This stage also introduces a **GitHub Actions workflow** (`.github/workflows/ci.yml`) for automated testing and linting.

* ✅ Runs `pytest` on every push and pull request
* ✅ Ensures code quality via `ruff` and optional `black` formatting
* ✅ Provides quick feedback in GitHub before merging

---

✅ With this stage complete, the project now has:

* A **data scientist's notebook** for preprocessing exploration (`01_data_preprocessing.ipynb`)
* A fully modular preprocessing pipeline in `src/data/`
* Automated tests and coverage
* Developer productivity tasks via Invoke
* Continuous integration checks via GitHub Actions

This clearly separates the **exploration stage** (notebooks) from the **engineering stage** (modules + CI/CD), setting the foundation for **exploratory data analysis (EDA)** in the next branch.