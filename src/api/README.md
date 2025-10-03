# **API Module — House Price Prediction**

This folder contains the **FastAPI service** that serves real-time and batch predictions for the **MLOps House Price Prediction** project.
It loads the trained estimator and preprocessor, validates inputs with Pydantic, performs inference, and returns structured JSON responses (including a simple ±10% confidence band).

The design follows **single-responsibility principles**:

* `schemas.py` → request/response Pydantic models
* `inference.py` → model/preprocessor loading + single/batch prediction logic
* `main.py` → FastAPI app, routing, CORS, and OpenAPI docs
* `requirements.txt` → lightweight runtime dependencies for the API layer

This keeps the API **modular, testable, and deployable**; it can run locally (Uvicorn), in containers, or be wired into CI/CD.

## **Module Structure**

```
src/api/
├── schemas.py         # Pydantic models (request & response)
├── inference.py       # Loads model/preprocessor and performs inference
├── main.py            # FastAPI app with /health, /predict, /batch-predict
└── requirements.txt   # API runtime dependencies
```

**Model artefacts expected:**

```
models/trained/
├── house_price_model.pkl
└── preprocessor.pkl
```

## **Endpoints**

### 1) `GET /health`

Quick liveness check.

* **Response**

  ```json
  { "status": "healthy", "model_loaded": true }
  ```

### 2) `POST /predict`

Single prediction.

* **Request** (`HousePredictionRequest`)

  ```json
  {
    "sqft": 1800.0,
    "bedrooms": 3,
    "bathrooms": 2.0,
    "location": "suburban",
    "year_built": 2005,
    "condition": "Good"
  }
  ```

* **Response** (`PredictionResponse`)

  ```json
  {
    "predicted_price": 352000.75,
    "confidence_interval": [316800.68, 387200.83],
    "features_importance": {},
    "prediction_time": "2025-10-03T18:30:12.345678"
  }
  ```

### 3) `POST /batch-predict`

Multiple predictions in one call.

* **Request** (`List[HousePredictionRequest]`)

  ```json
  [
    { "sqft": 1200, "bedrooms": 2, "bathrooms": 1.0, "location": "urban", "year_built": 1998, "condition": "Fair" },
    { "sqft": 2400, "bedrooms": 4, "bathrooms": 3.0, "location": "rural", "year_built": 2012, "condition": "Excellent" }
  ]
  ```
* **Response** (`List[float]`)

  ```json
  [245000.0, 421300.5]
  ```

## **Request/Response Schemas (summary)**

### `HousePredictionRequest`

* `sqft: float (>0)`
* `bedrooms: int (>=1)`
* `bathrooms: float (>0)`
* `location: str` (e.g., `"urban" | "suburban" | "rural"`)
* `year_built: int (1800–2023)`
* `condition: str` (e.g., `"Good" | "Excellent" | "Fair"`)

### `PredictionResponse`

* `predicted_price: float`
* `confidence_interval: List[float]` (two elements: `[lower, upper]`)
* `features_importance: Dict[str, float]` (empty by default)
* `prediction_time: str` (ISO-8601, UTC)

## **Running the API**

> Assumes you have the trained artefacts at `models/trained/house_price_model.pkl` and `models/trained/preprocessor.pkl`.

### Option A — Run with `uv`

```bash
# From project root
uv pip install -r src/api/requirements.txt
uv run uvicorn src.api.main:app --reload
```

Then open:

* [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) → **interactive Swagger UI**
* [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health) → **liveness check**

### Option B — Run with plain `pip`

```bash
pip install -r src/api/requirements.txt
uvicorn src.api.main:app --reload
```

## **Quick Usage**

### cURL

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sqft":1800,"bedrooms":3,"bathrooms":2.0,"location":"suburban","year_built":2005,"condition":"Good"}'
```

### HTTPie

```bash
http POST :8000/predict sqft:=1800 bedrooms:=3 bathrooms:=2.0 location=suburban year_built:=2005 condition=Good
```

### Python client

```python
import requests

payload = {
    "sqft": 1800,
    "bedrooms": 3,
    "bathrooms": 2.0,
    "location": "suburban",
    "year_built": 2005,
    "condition": "Good",
}
r = requests.post("http://127.0.0.1:8000/predict", json=payload, timeout=10)
print(r.json())
```

## **Configuration & Paths**

* **Model paths** are defined in `src/api/inference.py`:

  * `MODEL_PATH = "models/trained/house_price_model.pkl"`
  * `PREPROCESSOR_PATH = "models/trained/preprocessor.pkl"`
* If your deployment uses different locations (e.g., environment variables, mounted volumes), update these constants or read from env vars (recommended in production).

## **CORS**

`main.py` enables permissive CORS:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)
```

Tighten this for production by whitelisting origins (e.g., `["https://yourapp.example"]`).

## **Extending the API**

* **Confidence intervals**: Replace the ±10% band with model-based intervals (e.g., quantile regression, prediction intervals, conformal prediction).
* **Explainability**: Populate `features_importance` via tree importances or SHAP (add a flag to avoid heavy startup costs).
* **Batching & throughput**: Consider asynchronous queues (e.g., Celery/RQ) for large batches.
* **Validation**: Constrain categorical values for `location` and `condition` if the preprocessor expects a fixed vocabulary.

## ✅ Summary

This API module provides a **clean, production-ready** FastAPI layer for serving house-price predictions:

* Clear **schemas** and **separation of concerns**
* **Derived features** computed consistently with training
* Easy local run with `uv`/Uvicorn and interactive docs
* Sensible extension points for **explainability** and **intervals**

Plug it into your deployment pipeline and point it at your trained artefacts to go from **model** → **service** swiftly.
