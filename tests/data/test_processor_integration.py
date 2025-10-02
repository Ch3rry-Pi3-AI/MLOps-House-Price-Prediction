# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

from pathlib import Path

import pandas as pd

from src.data.config import ProcessorConfig
from src.data.processor import process_data


# -------------------------------------------------------------------
# Integration tests
# -------------------------------------------------------------------

def test_end_to_end_processing(tmp_path: Path):
    """
    End-to-end test of the data processing pipeline.

    Scenario
    --------
    - Input CSV contains a tight cluster of prices plus one extreme outlier.
    - Missing values present in `bedrooms` and `city`.
    - Run pipeline with outlier policy 'filter' and IQR multiplier 1.5.

    Expectations
    ------------
    - Output CSV is written to disk.
    - No missing values remain.
    - Exactly one row (the outlier) is removed.
    - Max price reflects the tight cluster (i.e., not the extreme outlier).
    """
    # Prepare a small input CSV: 5 tight values + 1 extreme outlier
    inp = tmp_path / "raw.csv"
    out = tmp_path / "processed.csv"
    df = pd.DataFrame(
        {
            "price": [100_000, 110_000, 115_000, 118_000, 120_000, 10_000_000],
            "bedrooms": [3, 2, 3, 4, 3, None],  # includes a missing
            "city": ["Leeds", "Leeds", "Leeds", "Leeds", "Leeds", None],  # missing
        }
    )
    df.to_csv(inp, index=False)

    # Run with 'filter' policy to remove the extreme outlier
    cfg = ProcessorConfig(target="price", outlier_policy="filter", iqr_multiplier=1.5)
    processed = process_data(str(inp), str(out), cfg)

    # Assertions
    assert out.exists(), "Processed CSV should be written."
    assert processed.isna().sum().sum() == 0, "No missing values after cleaning."
    assert len(processed) == len(df) - 1, "Exactly one row (the outlier) should be removed."
    assert processed["price"].max() < 1_000_000, "Max price should come from the tight cluster."
