# tests/data/test_processor_integration.py
import pandas as pd
from src.data.processor import process_data
from src.data.config import ProcessorConfig


def test_end_to_end_processing(tmp_path):
    # Prepare a small input CSV: 5 tight values + 1 extreme outlier
    inp = tmp_path / "raw.csv"
    out = tmp_path / "processed.csv"
    df = pd.DataFrame(
        {
            "price": [100_000, 110_000, 115_000, 118_000, 120_000, 10_000_000],
            "bedrooms": [3, 2, 3, 4, 3, None],  # includes a missing
            "city": [
                "Leeds",
                "Leeds",
                "Leeds",
                "Leeds",
                "Leeds",
                None,
            ],  # includes a missing
        }
    )
    df.to_csv(inp, index=False)

    # Run with 'filter' policy to remove the extreme outlier
    cfg = ProcessorConfig(target="price", outlier_policy="filter", iqr_multiplier=1.5)
    processed = process_data(str(inp), str(out), cfg)

    # Assertions
    assert out.exists(), "Processed CSV should be written"
    assert processed.isna().sum().sum() == 0, "No missing values after cleaning"

    # Expect outlier removed → dataset shrinks by exactly 1
    assert len(processed) == len(df) - 1

    # Sanity checks: the max should be from the tight cluster, not 10_000_000
    assert processed["price"].max() < 1_000_000
