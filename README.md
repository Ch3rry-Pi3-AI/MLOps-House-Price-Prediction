# **Exploratory Data Analysis (EDA) Stage**

This branch extends the **MLOps House Price Prediction** project by adding an **exploratory data analysis (EDA) notebook**.
The new notebook, `notebooks/02_eda.ipynb`, focuses on visual and statistical exploration of the dataset to identify trends, correlations, and potential issues.

Unlike the preprocessing stage, this work is **overwhelmingly a data scientist role**, so no Python modules are created in `src/` and no additional automation is required. The notebook serves as an analysis artefact to guide future modelling decisions.


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
│       └── cleaned_house_data.csv
├── deployment/
│   ├── kubernetes/
│   └── mlflow/
├── models/
│   └── trained/
├── notebooks/
│   ├── 01_data_preprocessing.ipynb  
│   └── 02_eda.ipynb                 # 🚀 NEW: Exploratory Data Analysis notebook
├── src/
│   ├── api/
│   ├── data/
│   ├── features/
│   └── models/
├── streamlit_app/
├── tests/
├── .gitignore
├── .python-version
├── pyproject.toml
├── README.md
├── requirements.txt
├── tasks.py
└── uv.lock
```

> Note: Any `.venv/` folder is ignored and should not be committed.


## **Development Environment**

This project continues to use [uv](https://github.com/astral-sh/uv) for Python environment and dependency management.
You will also need Docker for running MLflow locally and Kubernetes manifests for deployment.

### 1) Prerequisites

* [Python 3.13](https://www.python.org/downloads/)
* [Git](https://git-scm.com/)
* [Visual Studio Code](https://code.visualstudio.com/)
* [uv – Python package and environment manager](https://github.com/astral-sh/uv)
* [Docker Desktop](https://www.docker.com/products/docker-desktop)

### 2) Clone the repository

```bash
git clone https://github.com/<your-username>/MLOps-House-Price-Prediction.git
cd MLOps-House-Price-Prediction
```

### 3) Create and activate a virtual environment

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



## **Exploratory Data Analysis**

Run and explore the notebook:

```bash
notebooks/02_eda.ipynb
```

This notebook covers:

* Dataset inspection (shape, datatypes, missing values)
* Descriptive statistics
* Visualisation of price distributions
* Correlation analysis
* Scatter plots and categorical comparisons



✅ With this stage complete, the project now has:

* A dedicated **EDA notebook** for data scientist-driven analysis (`02_eda.ipynb`)
* Clear separation between **exploratory analysis** (notebooks) and **production pipelines** (modules + CI/CD)

This prepares the ground for **feature engineering** in the next branch.