# **Feature Engineering Modules**

This folder contains the **feature engineering pipeline** for the **MLOps House Price Prediction** project.
It extends the cleaned dataset from the **data preprocessing stage** with engineered features and a fitted scikit-learn preprocessing pipeline (saved as a `.pkl` file in `models/trained/`).

The design again follows **single-responsibility principles**:

* `builders.py` → feature logic & preprocessing components
* `processor.py` → orchestration (end-to-end run, persistence)
* `cli.py` → command-line access

This ensures a modular, testable, and extensible workflow that can be run directly, via CLI, or integrated into downstream model training.

## **Module Structure**

```
src/features/
├── builders.py     # Feature creation + preprocessor definition
├── processor.py    # Orchestrator for feature engineering pipeline
└── cli.py          # Command-line entrypoint
```

## **Module Overview (with build order)**

If building this folder **from scratch**, the natural order would be:

### 1. `builders.py` – Feature & Preprocessor Builders

* **Purpose**:

  * `create_features(df)`: add derived features (`house_age`, `price_per_sqft`, `bed_bath_ratio`).
  * `create_preprocessor()`: build a `ColumnTransformer` with numeric imputation and categorical one-hot encoding.
* **Dependencies**: `pandas`, `numpy`, `scikit-learn`, `logging`.
* **Why first**: Core logic that the processor depends on.

### 2. `processor.py` – Orchestrator

* **Purpose**:

  * Load cleaned CSV
  * Generate engineered features (`builders.create_features`)
  * Fit + transform features with preprocessor (`builders.create_preprocessor`)
  * Save the fitted preprocessor (`pickle`) to `models/trained/preprocessor.pkl`
  * Save the transformed dataset to CSV for model training
* **Dependencies**: `pandas`, `pickle`, `builders`.
* **Why second**: Ties feature creation and preprocessor definition into a full pipeline.

### 3. `cli.py` – Command-Line Entrypoint

* **Purpose**: Wraps `processor.run_feature_engineering` with `argparse`.
* **Features**: `--input`, `--output`, `--preprocessor` (defaults to `models/trained/preprocessor.pkl`).
* **Why last**: Provides user-facing execution once the pipeline exists.

## **Execution**

### 1. Direct Python Execution

```bash
python -m src.features.processor
```

This runs the pipeline with defaults (`data/processed/cleaned_house_data.csv` → `data/processed/engineered_features.csv`, saving preprocessor in `models/trained/preprocessor.pkl`).

### 2. Command-Line Interface

```bash
python -m src.features.cli \
  --input data/processed/cleaned_house_data.csv \
  --output data/processed/engineered_features.csv \
  --preprocessor models/trained/preprocessor.pkl
```

Overrides are supported (e.g. custom preprocessor path).

### 3. Invoke Task Runner

The repository also provides `tasks.py` with **Invoke** tasks. You can extend it with a `features` task:

```bash
invoke features
```

Defaults:

* **Input**: `data/processed/cleaned_house_data.csv`
* **Output**: `data/processed/engineered_features.csv`
* **Preprocessor**: `models/trained/preprocessor.pkl`

## ✅ Summary

This folder implements a **modular feature engineering stage** with:

* `builders.py` → reusable feature & preprocessor definitions
* `processor.py` → orchestration and persistence (CSV + pickle)
* `cli.py` → simple CLI interface
* Outputs saved consistently to `data/processed/` and `models/trained/`

The pipeline is **robust, testable, and production-ready**, providing engineered features and a reusable preprocessor for the final stage: **model training**.
