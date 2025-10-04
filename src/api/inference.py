# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------
from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Dict, List, Sequence

import joblib
import pandas as pd

from .schemas import HousePredictionRequest, PredictionResponse


# -------------------------------------------------------------------
# Model & Preprocessor Loading
# -------------------------------------------------------------------
MODEL_PATH = "models/trained/house_price_model.pkl"
PREPROCESSOR_PATH = "models/trained/preprocessor.pkl"

try:
    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
except Exception as e:
    raise RuntimeError(f"Error loading model or preprocessor: {str(e)}")


# -------------------------------------------------------------------
# Utilities
# -------------------------------------------------------------------
def _utc_now_iso() -> str:
    """Return current UTC time as ISO-8601 with 'Z' suffix."""
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _model_label(obj: object) -> str:
    """Return a short, human-friendly label for the model."""
    cls = getattr(obj, "__class__", type(obj))
    return getattr(cls, "__name__", "UnknownModel")


def _get_feature_names(preprocessor_obj) -> Sequence[str] | None:
    """
    Try to extract feature names produced by the preprocessor.

    Returns
    -------
    list[str] | None
        The transformed feature names if available (e.g., from ColumnTransformer),
        otherwise None.
    """
    try:
        names = preprocessor_obj.get_feature_names_out()
        # Ensure they are str for JSON serialisation
        return [str(n) for n in names]
    except Exception:
        return None


def _compute_feature_importance_map() -> Dict[str, float]:
    """
    Attempt to compute a feature-importance mapping from the loaded model.

    Strategy
    --------
    - If the model exposes ``feature_importances_``, map those against
      preprocessor-derived feature names (when available). If names are not
      available or lengths mismatch, fall back to generic ``f{i}`` labels.
    - Normalisation is not enforced; the UI can sort and display top-k.

    Returns
    -------
    dict[str, float]
        Mapping from transformed feature name to importance score.
        Returns an empty dict if importances are not available.
    """
    importances = getattr(model, "feature_importances_", None)
    if importances is None:
        return {}

    try:
        importances = [float(v) for v in importances]
    except Exception:
        return {}

    names = _get_feature_names(preprocessor)
    if names is None or len(names) != len(importances):
        # Fall back to generic labels
        return {f"f{i}": float(val) for i, val in enumerate(importances)}

    return {str(name): float(val) for name, val in zip(names, importances)}


# -------------------------------------------------------------------
# Public API
# -------------------------------------------------------------------
def predict_price(request: HousePredictionRequest) -> PredictionResponse:
    """
    Predict the house price for a single request.

    Parameters
    ----------
    request : HousePredictionRequest
        Validated input request containing house features.

    Returns
    -------
    PredictionResponse
        Structured response including:
        - ``predicted_price`` : float
            Predicted house price (rounded to 2 decimals).
        - ``confidence_interval`` : list[float]
            Lower and upper bounds of a ±10% band around the prediction.
        - ``features_importance`` : dict[str, float]
            Feature importances if the model exposes them; empty otherwise.
        - ``prediction_time`` : str
            ISO-8601 timestamp (UTC) of when the prediction was made.
        - ``prediction_duration`` : float
            Wall-clock time (seconds) to serve this prediction.
        - ``model`` : str
            Short label of the model used (e.g., ``"XGBRegressor"``).

    Notes
    -----
    - Adds derived features:
      ``house_age``, ``bed_bath_ratio``, and dummy ``price_per_sqft``.
    - Confidence interval is currently hard-coded at ±10%.
    """
    t0 = perf_counter()

    # Prepare input data
    input_data = pd.DataFrame([request.dict()])
    input_data["house_age"] = datetime.now().year - input_data["year_built"]
    input_data["bed_bath_ratio"] = input_data["bedrooms"] / input_data["bathrooms"]
    input_data["price_per_sqft"] = 0  # Dummy placeholder

    # Preprocess input
    processed_features = preprocessor.transform(input_data)

    # Predict
    predicted_price = model.predict(processed_features)[0]
    predicted_price = round(float(predicted_price), 2)

    # Confidence interval (±10%)
    confidence_interval = [
        round(float(predicted_price * 0.9), 2),
        round(float(predicted_price * 1.1), 2),
    ]

    # Feature importances (best-effort)
    fi_map = _compute_feature_importance_map()

    # Timing
    duration_s = perf_counter() - t0

    return PredictionResponse(
        predicted_price=predicted_price,
        confidence_interval=confidence_interval,
        features_importance=fi_map,
        prediction_time=_utc_now_iso(),
        prediction_duration=float(duration_s),
        model=_model_label(model),
    )


def batch_predict(requests: List[HousePredictionRequest]) -> List[float]:
    """
    Perform batch predictions on multiple requests.

    Parameters
    ----------
    requests : list[HousePredictionRequest]
        List of validated request objects.

    Returns
    -------
    list[float]
        Predicted prices (rounded by model precision).
    """
    input_data = pd.DataFrame([req.dict() for req in requests])
    input_data["house_age"] = datetime.now().year - input_data["year_built"]
    input_data["bed_bath_ratio"] = input_data["bedrooms"] / input_data["bathrooms"]
    input_data["price_per_sqft"] = 0  # Dummy placeholder

    # Preprocess
    processed_features = preprocessor.transform(input_data)

    # Predict
    predictions = model.predict(processed_features)
    return predictions.astype(float).round(2).tolist()


# -------------------------------------------------------------------
# Introspection helpers (optional)
# -------------------------------------------------------------------
def get_model_label() -> str:
    """
    Return a short label for the currently loaded model.

    Returns
    -------
    str
        Model class name or 'UnknownModel' if not available.
    """
    return _model_label(model)
