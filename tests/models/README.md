# **Test Suite — Model Training Modules (MLOps House Price Prediction)**

This folder contains the **unit and integration tests** for the **model training pipeline** of the **MLOps House Price Prediction** project.
It validates the **correctness**, **robustness**, and **end-to-end reliability** of all components under `src/models/`, including MLflow logging, model registration, and CLI orchestration.

Before running these tests, ensure that the **MLflow tracking server container** is running — it is required for the integration tests that involve model logging and registry operations.



## **MLflow Dependency**

The MLflow tracking server is containerised and configured under:

```
deployment/mlflow/docker-compose.yaml
```

You **must start this container first** before running any tests that touch the training pipeline.

### ⚙️ Start the MLflow container

From the project root:

```bash
cd deployment/mlflow
docker compose up -d
```

Verify it’s running:

```bash
docker ps
```

You should see a container mapping port `5555 → 5000`.
Then open:

👉 [http://localhost:5555](http://localhost:5555)

Once the MLflow UI is accessible, you can safely proceed to run the tests.



## **Test Structure**

```
tests/
├── conftest.py                                 # Shared root fixtures
├── models/
│   ├── conftest.py                             # Model-training specific fixture(s)
│   ├── test_builders_models.py                 # Unit: get_model_instance (estimator factory)
│   ├── test_config_training.py                 # Unit: YAML → dataclass loading
│   ├── test_processor_training_integration.py  # Integration: training + MLflow + registry
│   └── test_cli_models.py                      # CLI smoke test
```



## **Test Design (Layered Overview)**

The test suite follows **layered testing principles**, ensuring each level of abstraction is verified independently.

### 1️⃣ `conftest.py` — Shared Fixtures

Provides reusable **synthetic datasets** with numeric features and a target column `price`.
These datasets simulate realistic scenarios while keeping tests fast and lightweight.



### 2️⃣ `test_builders_models.py` — Model Builders

Unit tests for `get_model_instance` in `builders.py`.

**Checks:**

* Correct mapping of model names (`LinearRegression`, `RandomForest`, `GradientBoosting`, `XGBoost`)
* Unsupported names raise a `ValueError`
* Each estimator instance is initialised with the provided parameters



### 3️⃣ `test_config_training.py` — Configuration Loader

Unit tests for `config.load_training_config`.

**Checks:**

* YAML → dataclass conversion works as expected
* `TrainingConfig` and `ModelSection` fields are populated correctly
* Hyperparameters and target variable are preserved without mutation



### 4️⃣ `test_processor_training_integration.py` — Integration Tests

End-to-end testing for the **model training orchestration** (`processor.run_training`).

**Validates:**

* Engineered dataset with target `price` is loaded correctly
* Selected model trains without errors
* Metrics (MAE, R²) are computed and logged to MLflow
* Model and parameters are recorded in MLflow Tracking UI
* Model version is registered with alias `@staging` in MLflow Model Registry
* Trained model file is saved locally (`models/trained/{model_name}.pkl`)

> ⚠️ These tests require the **MLflow tracking container** to be running at
> `http://localhost:5555` (see setup instructions above).



### 5️⃣ `test_cli_models.py` — CLI Entrypoint Tests

Smoke tests for the command-line interface (`src.models.cli`).

**Validates:**

* CLI runs end-to-end with monkeypatched `sys.argv`
* Training completes and a `.pkl` model file is created
* No errors are raised when connecting to the MLflow tracking URI



## **Running Tests**

> 🧠 **Reminder:** Start the MLflow tracking container first:
>
> ```bash
> cd deployment/mlflow
> docker compose up -d
> ```
>
> Confirm it’s accessible at [http://localhost:5555](http://localhost:5555).



### 🔹 Run tests directly with `pytest`

From the project root:

```bash
pytest -q
```

Run only model training tests:

```bash
pytest tests/models -v
```

Run a specific test:

```bash
pytest tests/models/test_builders_models.py::test_get_model_instance_supported
```

Run with coverage:

```bash
pytest --cov=src --cov-report=term-missing
```



### 🔹 Run tests via Invoke Tasks

This project includes **Invoke task shortcuts** defined in `tasks.py`.

**Run all tests:**

```bash
invoke test
```

**Run only model-training tests:**

```bash
invoke test --path=tests/models
```

**Run with coverage:**

```bash
invoke cov
```

Other useful tasks:

| Task                       | Command        |
| -- | -- |
| Format code with Black     | `invoke fmt`   |
| Lint with Ruff             | `invoke lint`  |
| Clean caches and artefacts | `invoke clean` |



## ✅ **Summary**

This test suite ensures that the **model training pipeline** is:

| Category             | Guarantee                                                                 |
| -- | - |
| **Correct**          | Estimators and configurations behave as intended                          |
| **Robust**           | Integration tests confirm MLflow logging, registry, and local persistence |
| **Composable**       | Shared fixtures ensure consistent reproducibility                         |
| **Production-Ready** | CLI and orchestration are tested end-to-end                               |

Before executing tests, always ensure the **MLflow container** is running via:

```bash
cd deployment/mlflow
docker compose up -d
```

Then run your tests safely knowing all logging, metrics, and registry operations will be correctly tracked in
👉 [http://localhost:5555](http://localhost:5555).

This makes the **testing environment** fully aligned with the production-like **MLOps inference workflow**. 🚀
