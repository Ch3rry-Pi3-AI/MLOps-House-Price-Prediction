import pandas as pd
from src.data.io import load_csv, save_csv


def test_save_and_load_roundtrip(tmp_path):
    df = pd.DataFrame({"a": [1, 2, 3]})
    fp = tmp_path / "test.csv"
    save_csv(df, fp, index=False)
    df2 = load_csv(fp)
    pd.testing.assert_frame_equal(df2, df)
