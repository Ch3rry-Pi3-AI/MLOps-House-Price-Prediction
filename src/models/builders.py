# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------
from __future__ import annotations

from typing import Dict, Any, Type

from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import LinearRegression
import xgboost as xgb


# -------------------------------------------------------------------
# Public API
# -------------------------------------------------------------------

def get_model_instance(name: str, params: Dict[str, Any]):
    """
    Return an estimator instance given a model *name* and *params*.

    Notes
    -----
    Logic preserved exactly from the original script's `get_model_instance`.
    Supported names: "LinearRegression", "RandomForest", "GradientBoosting", "XGBoost".
    """
    model_map: Dict[str, Type] = {
        "LinearRegression": LinearRegression,
        "RandomForest": RandomForestRegressor,
        "GradientBoosting": GradientBoostingRegressor,
        "XGBoost": xgb.XGBRegressor,
    }
    if name not in model_map:
        raise ValueError(f"Unsupported model: {name}")
    return model_map[name](**params)