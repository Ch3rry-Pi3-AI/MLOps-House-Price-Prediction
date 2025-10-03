# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

from pathlib import Path
import pickle
import pandas as pd

from src.features.processor import run_feature_engineering


# -------------------------------------------------------------------
# Integration test
# -------------------------------------------------------------------

def test_end_to_end_feature_engineering(tmp_path: Path, df_features_minimal: pd.DataFrame):
    inp = tmp_path / "cleaned.csv"
    out = tmp_path / "engineered.csv"
    preproc = tmp_path / "models" / "trained" / "preprocessor.pkl"

    # Write input
    df_features_minimal.to_csv(inp, index=False)

    # Run pipeline (override default preprocessor path to stay in tmp)
    df_trans = run_feature_engineering(str(inp), str(out), str(preproc))

    # Files written
    assert out.exists(), "Engineered CSV should be written."
    assert preproc.exists(), "Preprocessor pickle should be written."

    # CSV readable and has target if present
    on_disk = pd.read_csv(out)
    assert len(on_disk) == len(df_features_minimal)
    assert "price" in on_disk.columns, "Target should be appended if present."

    # Pickle can be loaded and used
    with open(preproc, "rb") as f:
        pre = pickle.load(f)

    # Re-transform should produce the same number of rows
    X = df_features_minimal.copy()
    from src.features.builders import create_features  # local import to avoid circularity
    Xf = create_features(X).drop(columns=["price"])
    Xt = pre.transform(Xf)
    assert Xt.shape[0] == len(Xf)
