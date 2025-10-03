# **Test Suite**

This folder contains the **unit and integration tests** for the **MLOps House Price Prediction** project’s **model training pipeline**.
It validates the correctness, robustness, and consistency of all core modules under `src/models/`.

The test design follows **layered principles**:

* **Unit tests** check estimator instantiation (`builders.get_model_instance`) and configuration loading (`config.load_training_config`) in isolation.
* **Integration tests** validate the full training pipeline (`processor.run_training`) including MLflow logging, model registry, and local persistence.
* **CLI tests** ensure the command-line entrypoint runs correctly with monkeypatched arguments.
* **Fixtures** provide reusable synthetic datasets with a `price` target column.

All tests use **pytest** and can be run either **directly** or through **invoke tasks**.



## **Test Structure**

```
tests/
├── conftest.py                                 # Shared root fixtures
├── models/
│   ├── conftest.py                             # model-training specific fixture(s)
│   ├── test_builders_models.py                 # Tests for get_model_instance (estimator factory)
│   ├── test_config_training.py                 # Tests for config loading (YAML → dataclass)
│   ├── test_processor_training_integration.py  # End-to-end training with MLflow + registry
│   └── test_cli_models.py                      # CLI smoke test
```



## **Test Overview (with logical order)**

### 1. `conftest.py` – Fixtures

Provides reusable synthetic DataFrames with numeric features and a `price` target variable.
Ensures tests have realistic but lightweight datasets.



### 2. `test_builders_models.py` – Model Builders

Validates model instantiation:

* Correct mapping of names (`LinearRegression`, `RandomForest`, `GradientBoosting`, `XGBoost`) to scikit-learn/xgboost estimators.
* Unsupported names raise a `ValueError`.



### 3. `test_config_training.py` – Configuration Loader

Checks the YAML → dataclass conversion:

* Ensures `TrainingConfig` and `ModelSection` load correctly.
* Verifies hyperparameters and target variable are preserved.



### 4. `test_processor_training_integration.py` – Pipeline Orchestration

End-to-end test covering:

* Load engineered CSV with target `price`.
* Train the chosen model via `run_training`.
* Log parameters, metrics, and model to a **local MLflow tracking URI**.
* Register the model in the MLflow Model Registry with alias `@staging`.
* Save the trained model locally (`models/trained/{model}.pkl`).



### 5. `test_cli_models.py` – CLI Entrypoint

Smoke test for `src.models.cli.main()` with monkeypatched `sys.argv`:

* Confirms the CLI runs end-to-end.
* Asserts the trained `.pkl` model file is created.



## **Running Tests**

### 🔹 Direct pytest

From the project root:

```bash
pytest -q
```

Run only model-training tests:

```bash
pytest tests/models -v
```

Run a single test:

```bash
pytest tests/models/test_builders_models.py::test_get_model_instance_supported
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

* **Run only model training tests**:

  ```bash
  invoke test --path=tests/models
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

This test suite ensures the model training pipeline is:

* **Correct** – Estimators are created with the right parameters and config is parsed accurately.
* **Robust** – Integration tests validate MLflow logging, registry registration, and persistence.
* **Composable** – Shared fixtures provide consistent synthetic datasets.
* **Production-ready** – CLI and pipeline orchestration tests confirm the whole training workflow runs smoothly.

With both **pytest** and **invoke** support, contributors can run tests and quality checks with **short, memorable commands**.