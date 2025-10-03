# **Feature Engineering Modules**

This folder contains the **feature engineering pipeline** for the **MLOps House Price Prediction** project.
It extends the cleaned dataset from the **data preprocessing stage** with engineered features and a fitted scikit-learn preprocessing pipeline (saved as a `.pkl` file in `models/trained/`).

The design again follows **single-responsibility principles**:

* `builders.py` → feature logic & preprocessing components
* `processor.py` → orchestration (end-to-end run, persistence)
* `config.py` → configuration dataclass + YAML loader
* `cli.py` → command-line access

This ensures a modular, testable, and extensible workflow that can be run directly, via CLI/YAML, or integrated into downstream model training.

## **Module Structure**

```
src/features/
├── builders.py     # Feature creation + preprocessor definition
├── processor.py    # Orchestrator for feature engineering pipeline
├── config.py       # FeaturesConfig dataclass + YAML loader
└── cli.py          # Command-line entrypoint (flags + YAML)
```

## **Module Overview (with build order)**

If building this folder **from scratch**, the natural order would be:

### 1. `builders.py` – Feature & Preprocessor Builders

* **Purpose**

  * `create_features(df)`: add derived features (`house_age`, `price_per_sqft`, `bed_bath_ratio`).
  * `create_preprocessor()`: build a `ColumnTransformer` with numeric imputation and categorical one-hot encoding.
* **Dependencies**: `pandas`, `numpy`, `scikit-learn`, `logging`.
* **Why first**: Core logic that the processor depends on.

### 2. `processor.py` – Orchestrator

* **Purpose**

  * Load cleaned CSV
  * Generate engineered features (`builders.create_features`)
  * Fit + transform features with preprocessor (`builders.create_preprocessor`)
  * Save the fitted preprocessor (`pickle`) to `models/trained/preprocessor.pkl`
  * Save the transformed dataset to CSV for model training
* **Dependencies**: `pandas`, `pickle`, `builders`.
* **Why second**: Ties feature creation and preprocessor definition into a full pipeline.

### 3. `config.py` – Configuration

* **Purpose**

  * `FeaturesConfig` (frozen dataclass) holding `input`, `output`, `preprocessor` paths
  * `load_features_config(path)` to load YAML into `FeaturesConfig`
* **Why third**: Centralises execution parameters for both CLI and programmatic use.

### 4. `cli.py` – Command-Line Entrypoint

* **Purpose**: Wraps `processor.run_feature_engineering` with `argparse`.
* **Features**:

  * Flags: `--input`, `--output`, `--preprocessor`
  * YAML: `--config engineer.yaml`
  * **Precedence**: CLI flags override YAML; if still unset, `preprocessor` defaults to `models/trained/preprocessor.pkl`
* **Why last**: Provides user-facing execution once the pipeline exists.

## **Execution**

### 1. Direct Python Execution

```bash
python -m src.features.processor
```

Runs with defaults (`data/processed/cleaned_house_data.csv` → `data/processed/engineered_features.csv`, preprocessor to `models/trained/preprocessor.pkl`).

### 2. Command-Line Interface

Run with explicit flags:

```bash
python -m src.features.cli \
  --input data/processed/cleaned_house_data.csv \
  --output data/processed/engineered_features.csv \
  --preprocessor models/trained/preprocessor.pkl
```

Run with YAML config (`engineer.yaml`):

```bash
python -m src.features.cli --config=engineer.yaml
```

**CLI precedence**

1. Load defaults from `engineer.yaml` (if provided).
2. Override with any explicit flags (`--input/--output/--preprocessor`).
3. If `preprocessor` remains unset, default to `models/trained/preprocessor.pkl`.

### 3. Invoke Task Runner

Run with defaults:

```bash
invoke features
```

Run pipeline only (skip tests):

```bash
invoke engineer
```

Run with custom paths:

```bash
invoke features --input=data/processed/cleaned_house_data.csv \
                --output=data/processed/engineered_features.csv \
                --preprocessor=models/trained/preprocessor.pkl
```

## **YAML Configuration**

Create `engineer.yaml` in the project root:

```yaml
# engineer.yaml
input: data/processed/cleaned_house_data.csv
output: data/processed/engineered_features.csv
preprocessor: models/trained/preprocessor.pkl
```

Use it via:

```bash
python -m src.features.cli --config=engineer.yaml
```



## ✅ Summary

This folder implements a **modular feature engineering stage** with:

* `builders.py` → reusable feature & preprocessor definitions
* `processor.py` → orchestration and persistence (CSV + pickle)
* `config.py` → centralised configuration with a YAML loader
* `cli.py` → simple CLI with flags + YAML support (`engineer.yaml`)
* Outputs saved consistently to `data/processed/` and `models/trained/`

The pipeline is **robust, testable, and production-ready**, providing engineered features and a reusable preprocessor for the final stage: **model training**.
