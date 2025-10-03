# **Test Suite**

This folder contains the **unit and integration tests** for the **MLOps House Price Prediction** project’s feature engineering pipeline.
It validates the correctness, robustness, and consistency of all core modules under `src/features/`.

The test design follows **layered principles**:

* **Unit tests** check feature creation (`builders.create_features`) and preprocessor setup (`builders.create_preprocessor`) in isolation.
* **Integration tests** validate the full pipeline (`processor.run_feature_engineering`).
* **CLI tests** ensure the command-line entrypoint runs correctly.
* **Fixtures** provide reusable, well-defined datasets with edge cases (division by zero, unseen categories, etc.).

All tests use **pytest** and can be run either **directly** or through **invoke tasks**.

## **Test Structure**

```
tests/
├── conftest.py                         # Shared root fixtures
├── features/
│   ├── conftest.py                     # Feature-engineering specific fixtures
│   ├── test_builders_features.py       # Tests for create_features (engineered cols)
│   ├── test_builders_preprocessor.py   # Tests for create_preprocessor (transformer)
│   ├── test_processor_integration.py   # End-to-end pipeline (CSV + pickle)
│   └── test_cli.py                     # CLI smoke test
```

## **Test Overview (with logical order)**

### 1. `conftest.py` – Fixtures

Reusable small DataFrames with numeric/categorical values and edge cases (e.g. `bathrooms=0`).

### 2. `test_builders_features.py` – Feature Creation

Validates new engineered features:

* `house_age` → current year minus `year_built`
* `price_per_sqft` → price divided by sqft
* `bed_bath_ratio` → bedrooms/bathrooms with inf/NaN handled

### 3. `test_builders_preprocessor.py` – Preprocessor Builder

Ensures the `ColumnTransformer`:

* Correctly imputes numerics and encodes categoricals
* Ignores unseen categories at transform-time

### 4. `test_processor_integration.py` – Pipeline Orchestration

End-to-end test covering:

* Load cleaned CSV
* Generate engineered features
* Fit + save preprocessor (`pickle`) to `models/trained/`
* Save transformed dataset to CSV
* Reload pickle and reuse transformer

### 5. `test_cli.py` – CLI Entrypoint

Smoke test for `src.features.cli.main()` with monkeypatched argv.

## **Running Tests**

### 🔹 Direct pytest

From the project root:

```bash
pytest -q
```

Run only feature-engineering tests:

```bash
pytest tests/features -v
```

Run a single test:

```bash
pytest tests/features/test_builders_features.py::test_create_features_handles_division_edge_cases
```

With coverage:

```bash
pytest --cov=src --cov-report=term-missing
```

### 🔹 Via Invoke Tasks

This project provides **invoke shortcuts** defined in `tasks.py`.

* **Run all tests**:

  ```bash
  invoke test
  ```

* **Run only feature engineering tests**:

  ```bash
  invoke test --path=tests/features
  ```

* **Run with coverage**:

  ```bash
  invoke cov
  ```

Other useful tasks:

* **Format code with Black** → `invoke fmt`
* **Lint with Ruff** → `invoke lint`
* **Clean caches and artefacts** → `invoke clean`

## ✅ Summary

This test suite ensures the feature engineering pipeline is:

* **Correct** – Engineered columns are computed as expected.
* **Robust** – Handles edge cases like division by zero and unseen categories.
* **Composable** – Shared fixtures provide consistent test data.
* **Production-ready** – Integration tests confirm persistence of both transformed CSVs and the pickled preprocessor.

With both **pytest** and **invoke** support, contributors can run tests and quality checks with **short, memorable commands**.