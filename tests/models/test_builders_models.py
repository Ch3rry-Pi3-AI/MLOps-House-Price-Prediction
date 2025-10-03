# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------
import pytest
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
import xgboost as xgb

from src.models.builders import get_model_instance


# -------------------------------------------------------------------
# Tests: get_model_instance
# -------------------------------------------------------------------

@pytest.mark.parametrize(
    "name, cls",
    [
        ("LinearRegression", LinearRegression),
        ("RandomForest", RandomForestRegressor),
        ("GradientBoosting", GradientBoostingRegressor),
        ("XGBoost", xgb.XGBRegressor),
    ],
)
def test_get_model_instance_supported(name, cls):
    model = get_model_instance(name, params={})
    assert isinstance(model, cls)


def test_get_model_instance_unsupported():
    with pytest.raises(ValueError):
        get_model_instance("TotallyNotAThing", params={})