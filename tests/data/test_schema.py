# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

import numpy as np
import pandas as pd
import pytest

from src.data.schema import is_numeric, require_columns


# -------------------------------------------------------------------
# Schema validation tests
# -------------------------------------------------------------------

def test_require_columns_pass():
    """
    `require_columns` should pass silently when all columns are present.
    """
    df = pd.DataFrame({"a": [1], "b": [2]})
    require_columns(df, ["a", "b"])  # should not raise


def test_require_columns_fail():
    """
    `require_columns` should raise a ValueError when required columns are missing.
    """
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(ValueError) as e:
        require_columns(df, ["a", "b"])
    assert "Missing required columns" in str(e.value)


def test_is_numeric():
    """
    `is_numeric` should correctly identify numeric Series.
    """
    df = pd.DataFrame(
        {
            "x": [1, 2],             # int
            "y": ["a", "b"],         # str
            "z": np.array([1.0, 2.0])  # float
        }
    )
    assert is_numeric(df["x"]) is True
    assert is_numeric(df["z"]) is True
    assert is_numeric(df["y"]) is False
