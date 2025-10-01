import pandas as pd
import pytest
from src.data.schema import require_columns, is_numeric


def test_require_columns_pass():
    df = pd.DataFrame({"a": [1], "b": [2]})
    require_columns(df, ["a", "b"])  # should not raise


def test_require_columns_fail():
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(ValueError) as e:
        require_columns(df, ["a", "b"])
    assert "Missing required columns" in str(e.value)


def test_is_numeric():
    import numpy as np

    df = pd.DataFrame({"x": [1, 2], "y": ["a", "b"], "z": np.array([1.0, 2.0])})
    assert is_numeric(df["x"]) is True
    assert is_numeric(df["z"]) is True
    assert is_numeric(df["y"]) is False
