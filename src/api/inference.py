# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------
from __future__ import annotations

from datetime import datetime
from typing import List

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
        - ``predicted_price``: float
            Predicted house price (rounded to 2 decimals).
        - ``confidence_interval``: list[float]
            Lower and upper bounds of the 90-110% confidence band.
        - ``features_importance``: dict
            Currently empty placeholder. Can be extended to return
            feature importances from tree-based models.
        - ``prediction_time``: str
            ISO-8601 timestamp of prediction.

    Notes
    -----
    - Adds derived features:
      ``house_age``, ``bed_bath_ratio``, and dummy ``price_per_sqft``.
    - Confidence interval is currently hard-coded at ±10%.
    """
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

    return PredictionResponse(
        predicted_price=predicted_price,
        confidence_interval=confidence_interval,
        features_importance={},  # Optional extension
        prediction_time=datetime.now().isoformat(),
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