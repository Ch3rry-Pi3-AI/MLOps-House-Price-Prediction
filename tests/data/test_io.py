# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

import pandas as pd

from src.data.io import load_csv, save_csv


# -------------------------------------------------------------------
# Tests
# -------------------------------------------------------------------

def test_save_and_load_roundtrip(tmp_path):
    """
    Ensure that saving a DataFrame to CSV and reloading produces the same data.

    Expectations
    ------------
    - The saved file can be reloaded without error.
    - The reloaded DataFrame matches the original exactly.
    """
    df = pd.DataFrame({"a": [1, 2, 3]})
    fp = tmp_path / "test.csv"

    save_csv(df, fp, index=False)
    df2 = load_csv(fp)

    pd.testing.assert_frame_equal(df2, df)
