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
* **Dependencies**:

  * `pandas` for reading/writing tabular data.
  * `pathlib.Path` for safe cross-platform file paths.
  * `logging` for visibility.
* **Why first**: Provides the fundamental load/save functions used everywhere else.

### 2. `schema.py` – Schema Validation

* **Purpose**: Ensure required columns exist and check types (numeric vs categorical).
* **Dependencies**:

  * `pandas.api.types` for dtype checks.
  * `logging` for schema-related errors/warnings.
* **Why second**: Guarantees that all downstream steps have the columns they expect.

### 3. `cleaning.py` – Missing Value Imputation

* **Purpose**: Impute missing values:

  * **Numeric** → median
  * **Categorical** → mode (or `"UNKNOWN"`)
* **Dependencies**:

  * Relies on `schema.is_numeric` from **schema.py**.
  * Uses `pandas` for Series-level operations.
  * `logging` for imputation audit trail.
* **Why third**: Missing values must be handled before outlier detection.

### 4. `outliers.py` – Outlier Handling

* **Purpose**: Detect and handle outliers using the **Interquartile Range (IQR) rule**.

  * `iqr_bounds`: Compute thresholds.
  * `apply_outlier_policy`: Apply `"filter"`, `"clip"`, or `"none"`.
* **Dependencies**:

  * `pandas` for calculations.
  * `logging` for reporting removed/clipped outliers.
* **Why fourth**: Outlier handling builds on a clean dataset.

### 5. `config.py` – Configuration Management

* **Purpose**: Centralise pipeline parameters using a frozen `@dataclass`.
* **Features**:

  * Default target (`price`)
  * Outlier policy (`filter`, `clip`, or `none`)
  * IQR multiplier
  * Save index toggle
  * Optional YAML loader (`pyyaml`) for externalised configs.
* **Why fifth**: Encapsulates pipeline parameters, making the processor and CLI configurable.

### 6. `processor.py` – Orchestrator

* **Purpose**: The **glue module** that ties all the above steps into a linear pipeline:

  1. Load raw CSV (from `io.py`)
  2. Validate schema (from `schema.py`)
  3. Impute missing values (from `cleaning.py`)
  4. Apply outlier policy (from `outliers.py`)
  5. Save processed CSV (via `io.py`)
* **Dependencies**:

  * Imports all other modules in this folder.
  * Uses `logging` for end-to-end visibility.
* **Why sixth**: The orchestrator comes after all supporting modules are ready.

### 7. `cli.py` – Command-Line Entrypoint

* **Purpose**: Expose the pipeline to end users via `argparse`.
* **Features**:

  * Accepts `--in`, `--out`, `--config` (YAML), `--policy`, and `--target`.
  * Allows overriding config values without editing code.
* **Dependencies**:

  * `argparse` for CLI parsing.
  * `config.py` for defaults and YAML configs.
  * `processor.py` for running the pipeline.
* **Why last**: Built once the processing pipeline is stable, providing user-facing access.

## **Execution**

You can run preprocessing directly:

```bash
python -m src.data.processor
```

Or via the CLI:

```bash
python -m src.data.cli --in data/raw/house_data.csv --out data/processed/cleaned_house_data.csv --policy filter
```

The CLI supports optional overrides:

```bash
# Use a YAML config file
python -m src.data.cli --in data/raw/house_data.csv --out data/processed/cleaned_house_data.csv --config=config.yaml

# Override policy & target on the fly
python -m src.data.cli --in data/raw/house_data.csv --out data/processed/cleaned_house_data.csv --policy clip --target SalePrice
```

## ✅ Summary

This folder implements a **modular preprocessing stage** with:

* Dedicated modules for **I/O, schema checks, cleaning, outlier handling, configuration, orchestration, and CLI**.
* Clear separation of concerns and minimal dependencies.
* Extensibility for future additions (e.g. scaling, encoding).
* Both **library-style** usage (importing `process_data`) and **CLI execution**.

This structure ensures the pipeline is **robust, testable, and production-ready**, forming the foundation for the **feature engineering stage**.
