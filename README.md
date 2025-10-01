# **Initial Project Setup**

This branch establishes the initial project structure for the **MLOps House Price Prediction** project. It contains a minimal Python package under `src/`, with other folders prepared for data, deployment, model training, and application development. No data import modules are included in this branch.

## **Project Structure**

```
mlops-house-price-prediction/
├── .venv/                  # Local virtual environment (ignored in Git)
├── data/
│   ├── raw/                # Raw datasets
│   └── processed/          # Cleaned / transformed datasets
├── deployment/
│   ├── kubernetes/         # Deployment manifests for Kubernetes
│   └── mlflow/             # MLflow tracking server setup
├── models/
│   └── trained/            # Trained models and preprocessing artefacts
├── notebooks/              # Jupyter notebooks (exploration, experiments)
├── src/
│   ├── api/                # API endpoints for serving predictions
│   ├── data/               # Data handling modules
│   ├── features/           # Feature engineering pipeline
│   └── models/             # Model training and evaluation scripts
├── streamlit_app/          # Streamlit application for model interaction
├── .gitignore              # Ignore rules for Git
├── .python-version         # Python version pin (for uv/pyenv)
├── pyproject.toml          # Project metadata and build configuration
├── README.md               # Project documentation (you are here)
├── requirements.txt        # Python dependencies
├── tasks.py                # Task runner / automation entry point
└── uv.lock                 # uv lockfile for reproducible installs
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
