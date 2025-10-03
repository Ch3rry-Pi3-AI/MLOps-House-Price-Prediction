# **Data Preprocessing Modules**

This folder contains the **data preprocessing pipeline** for the **MLOps House Price Prediction** project.
It provides a modular, testable, and extensible structure for turning raw input data into a cleaned dataset that is ready for downstream feature engineering and model training.

The design follows **single-responsibility principles**: each module handles one clear task (I/O, schema validation, cleaning, outlier handling, orchestration, etc.).
Together, they form a flexible preprocessing pipeline that can be run directly, via CLI, or integrated into larger workflows.



## **Module Structure**

```
src/data/
├── cleaning.py      # Missing value handling
├── config.py        # Config dataclass + optional YAML loader
├── io.py            # CSV load & save helpers
├── outliers.py      # Outlier detection & handling policies
├── processor.py     # Orchestrator for preprocessing pipeline
├── schema.py        # Schema/column validation utilities
└── cli.py           # Command-line entrypoint
```



## **Module Overview (with build order)**

If building this folder **from scratch**, the natural order would be:

### 1. `io.py` – Input/Output Helpers

* **Purpose**: Standardise CSV reading/writing.
* **Dependencies**: `pandas`, `pathlib.Path`, `logging`.
* **Why first**: Provides the fundamental load/save functions used everywhere else.

### 2. `schema.py` – Schema Validation

* **Purpose**: Ensure required columns exist and check types.
* **Dependencies**: `pandas.api.types`, `logging`.
* **Why second**: Guarantees that downstream steps have the expected structure.

### 3. `cleaning.py` – Missing Value Imputation

* **Purpose**: Impute missing values (numeric → median, categorical → mode or `"UNKNOWN"`).
* **Dependencies**: `schema.is_numeric`, `pandas`, `logging`.
* **Why third**: Missing values must be resolved before outlier handling.

### 4. `outliers.py` – Outlier Handling

* **Purpose**: Detect and handle outliers using the **IQR rule** (`filter`, `clip`, or `none`).
* **Dependencies**: `pandas`, `logging`.
* **Why fourth**: Outlier policies build on clean, imputed data.

### 5. `config.py` – Configuration Management

* **Purpose**: Centralise parameters in a frozen `@dataclass`.
* **Features**: default target, outlier policy, IQR multiplier, save index toggle, YAML loader.
* **Why fifth**: Encapsulates pipeline parameters for both code and CLI.

### 6. `processor.py` – Orchestrator

* **Purpose**: Tie together the pipeline:

  1. Load CSV (`io`)
  2. Validate schema (`schema`)
  3. Impute missing values (`cleaning`)
  4. Apply outlier policy (`outliers`)
  5. Save cleaned CSV (`io`)
* **Dependencies**: All other modules, `logging`.
* **Why sixth**: Built once the supporting modules exist.

### 7. `cli.py` – Command-Line Entrypoint

* **Purpose**: Expose the pipeline with `argparse`.
* **Features**: `--in`, `--out`, `--config`, `--policy`, `--target`.
* **Dependencies**: `argparse`, `config.py`, `processor.py`.
* **Why last**: Provides user-facing access once the processor is ready.



## **Execution**

### 1. Direct Python Execution

```bash
python -m src.data.processor
```

This runs the pipeline with defaults (`data/raw/house_data.csv` → `data/processed/cleaned_house_data.csv`).



### 2. Command-Line Interface

```bash
python -m src.data.cli --in data/raw/house_data.csv --out data/processed/cleaned_house_data.csv --policy filter
```

Optional overrides:

```bash
# Use a YAML config
python -m src.data.cli --in data/raw/house_data.csv --out data/processed/cleaned_house_data.csv --config=clean.yaml

# Override policy & target on the fly
python -m src.data.cli --in data/raw/house_data.csv --out data/processed/cleaned_house_data.csv --policy clip --target price
```



### 3. Invoke Task Runner

The repository also provides `tasks.py` with an **Invoke**-based task runner.

#### Install Invoke

```bash
uv pip install invoke
```

#### Ensure directories

```bash
invoke ensure-dirs
```

This creates `data/raw/`, `data/processed/`, and `models/trained/` if they don’t exist.

#### Run preprocessing (defaults)

```bash
invoke preprocess
```

Defaults:

* **Input**: `data/raw/house_data.csv`
* **Output**: `data/processed/cleaned_house_data.csv`
* **Policy**: `filter`
* **Target**: `price`
* **IQR**: `1.5`
* **Index**: `false`

#### Run preprocessing with overrides

```bash
# Clip outliers on SalePrice with wider IQR
invoke preprocess --policy=clip --target=SalePrice --iqr=2.0

# Save index column and custom output path
invoke preprocess --output=data/processed/saleprice_clean.csv --index=true

# Process a different input file
invoke preprocess --input=data/raw/new_house_data.csv
```



## ✅ Summary

This folder implements a **modular preprocessing stage** with:

* Dedicated modules for **I/O, schema checks, cleaning, outlier handling, configuration, orchestration, and CLI**.
* Flexible execution via **direct Python**, **CLI**, or **Invoke tasks**.
* Clear separation of concerns and minimal dependencies.
* Extensibility for future additions (scaling, encoding, feature engineering).

The pipeline is **robust, testable, and production-ready**, forming the foundation for the next stage: **feature engineering**.