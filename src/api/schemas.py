# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------
from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel, Field


# -------------------------------------------------------------------
# Data Models
# -------------------------------------------------------------------
class HousePredictionRequest(BaseModel):
    """
    Request payload for a single house-price prediction.

    Parameters
    ----------
    sqft : float
        Square footage of the house. Must be strictly greater than 0.
    bedrooms : int
        Number of bedrooms. Must be at least 1.
    bathrooms : float
        Number of bathrooms (can be fractional, e.g., 1.5). Must be strictly greater than 0.
    location : str
        Categorical location descriptor (e.g., ``"urban"``, ``"suburban"``, ``"rural"``).
    year_built : int
        Year the property was built. Constrained to be between 1800 and 2023 (inclusive).
    condition : str
        Overall condition of the property (e.g., ``"Good"``, ``"Excellent"``, ``"Fair"``).

    Notes
    -----
    - This schema is intentionally minimal and model-agnostic; it does not
      enforce a fixed label set for ``location`` or ``condition``.
    - If your downstream model expects encoded categories, ensure the API
      layer performs the correct mapping prior to inference.
    """

    sqft: float = Field(..., gt=0, description="Square footage of the house (> 0).")
    bedrooms: int = Field(..., ge=1, description="Number of bedrooms (>= 1).")
    bathrooms: float = Field(..., gt=0, description="Number of bathrooms (> 0).")
    location: str = Field(..., description='Location category, e.g. "urban", "suburban", "rural".')
    year_built: int = Field(
        ...,
        ge=1800,
        le=2023,
        description="Construction year (between 1800 and 2023, inclusive).",
    )
    condition: str = Field(..., description='Condition label, e.g. "Good", "Excellent", "Fair".')


class PredictionResponse(BaseModel):
    """
    Response payload returned by the prediction endpoint.

    Parameters
    ----------
    predicted_price : float
        Point estimate of the predicted sale price (in the model's currency units).
    confidence_interval : List[float]
        Two-element list ``[lower, upper]`` representing the uncertainty band
        around ``predicted_price``. The confidence level is model-defined.
    features_importance : Dict[str, float]
        Mapping from feature name to importance score (normalisation is model-specific).
    prediction_time : str
        ISO-8601 timestamp (UTC) when the prediction was generated.
    prediction_duration : float
        Wall-clock inference time in **seconds** for serving this prediction.
    model : str
        A short label for the model used to generate the prediction (e.g., ``"XGBRegressor"``).

    Notes
    -----
    - ``features_importance`` may be empty when the underlying model does not
      expose importances (e.g., plain linear regression without post-hoc methods).
    - ``prediction_time`` is a string for portability; ``prediction_duration`` is numeric
      to support UI metrics (seconds).
    """

    predicted_price: float = Field(..., description="Point estimate of the predicted price.")
    confidence_interval: List[float] = Field(
        ...,
        min_items=2,
        max_items=2,
        description="Two-element list [lower, upper] for the confidence interval.",
    )
    features_importance: Dict[str, float] = Field(
        default_factory=dict,
        description="Feature importance mapping (name -> score).",
    )
    prediction_time: str = Field(..., description="ISO-8601 UTC timestamp of prediction.")
    prediction_duration: float = Field(..., ge=0.0, description="Wall-clock inference time in seconds.")
    model: str = Field(..., description="Model label used for this prediction.")
