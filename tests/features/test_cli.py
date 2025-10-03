# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

import sys
from pathlib import Path
import pandas as pd
import types

from src.features import cli as features_cli


# -------------------------------------------------------------------
# CLI test
# -------------------------------------------------------------------

def test_cli_invocation(tmp_path, monkeypatch, df_features_minimal):
    inp = tmp_path / "cleaned.csv"
    out = tmp_path / "engineered.csv"
    pre = tmp_path / "models" / "trained" / "preprocessor.pkl"

    df_features_minimal.to_csv(inp, index=False)

    # Monkeypatch argv for argparse
    argv = [
        "python",
        "--input", str(inp),
        "--output", str(out),
        "--preprocessor", str(pre),
    ]
    monkeypatch.setattr(sys, "argv", argv)

    # Run CLI main
    features_cli.main()

    # Outputs should exist
    assert out.exists()
    assert pre.exists()

    # Engineered CSV should have same rows as input
    on_disk = pd.read_csv(out)
    assert len(on_disk) == len(df_features_minimal)
