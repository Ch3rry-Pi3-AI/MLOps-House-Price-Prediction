# **Test Suite**

This folder contains the **unit and integration tests** for the **MLOps House Price Prediction** project’s data preprocessing pipeline.
It validates the correctness, robustness, and consistency of all core modules under `src/data/`.

The test design follows **layered principles**:

* **Unit tests** check each module in isolation (I/O, schema, cleaning, outliers).
* **Integration tests** validate the full pipeline (processor orchestration).
* **Fixtures** provide reusable, well-defined datasets with edge cases (missing values, outliers, mixed dtypes).

All tests use **pytest** and can be run either **directly** or through **invoke tasks**.



## **Test Structure**

```
tests/
├── conftest.py                         # Shared fixtures (small synthetic DataFrames)
├── data/
│   ├── test_cleaning.py                # Tests for missing value imputation
│   ├── test_io.py                      # Tests for CSV save/load roundtrip
│   ├── test_outliers.py                # Tests for IQR bounds & outlier policies
│   ├── test_processor_integration.py   # End-to-end integration test of pipeline
│   └── test_schema.py                  # Tests for schema validation & numeric checks
```



## **Test Overview (with logical order)**

### 1. `conftest.py` – Fixtures

Reusable small DataFrames with mixed types, missing values, and outliers.

### 2. `test_io.py` – I/O

Ensures CSV save/load roundtrips are lossless.

### 3. `test_schema.py` – Schema Validation

Checks required columns and numeric detection.

### 4. `test_cleaning.py` – Missing Value Imputation

Validates numeric median + categorical mode imputation.

### 5. `test_outliers.py` – Outlier Handling

Covers `"filter"`, `"clip"`, and `"none"` policies.

### 6. `test_processor_integration.py` – Pipeline Orchestration

End-to-end test of loading, cleaning, outlier filtering, and saving.



## **Running Tests**

### 🔹 Direct pytest

From the project root:

```bash
pytest -q
```

Run a specific file:

```bash
pytest tests/data/test_outliers.py -v
```

With coverage:

```bash
pytest --cov=src --cov-report=term-missing
```



### 🔹 Via Invoke Tasks

This project provides **invoke shortcuts** defined in `tasks.py` for consistent workflows.

* **Run all tests**:

  ```bash
  invoke test
  ```

  Options:

  * `-k "<expr>"` → only run tests matching expression
  * `-m "<marker>"` → only run tests with given marker
  * `--path <dir>` → run tests from a subdirectory

* **Run with coverage**:

  ```bash
  invoke cov
  ```

* **Format code with Black**:

  ```bash
  invoke fmt
  ```

* **Lint with Ruff**:

  ```bash
  invoke lint
  ```

* **Clean caches and artefacts**:

  ```bash
  invoke clean
  ```



## ✅ Summary

This test suite ensures the preprocessing pipeline is:

* **Correct** – Validates individual transformations.
* **Robust** – Handles missing values, schema issues, and outliers.
* **Composable** – Shared fixtures provide consistent test data.
* **Production-ready** – Integration tests confirm full pipeline behaviour.

With both **pytest** and **invoke** support, contributors can run tests and quality checks with **short, memorable commands**.