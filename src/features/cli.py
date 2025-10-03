# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

import argparse
from .processor import run_feature_engineering
from .config import load_features_config, FeaturesConfig


# -------------------------------------------------------------------
# Argument parsing
# -------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the feature engineering stage.

    Returns
    -------
    argparse.Namespace
        Parsed arguments with attributes: inp, out, preproc, config.
    """
    p = argparse.ArgumentParser(description="Feature engineering for housing data")
    p.add_argument("--input", dest="inp", help="Path to cleaned CSV file")
    p.add_argument("--output", dest="out", help="Path for output CSV file (engineered features)")
    p.add_argument(
        "--preprocessor",
        dest="preproc",
        help="Path for saving the preprocessor (pickle). "
             "If omitted, falls back to YAML config or 'models/trained/preprocessor.pkl'."
    )
    p.add_argument("--config", help="Path to YAML config file for feature engineering")
    return p.parse_args()


# -------------------------------------------------------------------
# Main entry point
# -------------------------------------------------------------------

def main():
    """
    Execute the feature engineering pipeline from CLI arguments.

    Precedence
    ----------
    1) If --config is provided, load defaults from YAML.
    2) Any explicit CLI flags (--input/--output/--preprocessor) override YAML values.
    3) preprocessor defaults to 'models/trained/preprocessor.pkl' if still unset.

    Exits with a helpful error message if input/output are missing after applying
    the above precedence.
    """
    args = parse_args()

    # Start from YAML (if provided) or dataclass defaults
    cfg: FeaturesConfig = load_features_config(args.config) if args.config else FeaturesConfig()

    # CLI overrides (only if provided)
    inp = args.inp or cfg.input
    out = args.out or cfg.output
    preproc = args.preproc or cfg.preprocessor or "models/trained/preprocessor.pkl"

    # Validate required paths
    if not inp or not out:
        raise SystemExit(
            "Error: You must provide --input and --output, either directly or via --config."
        )

    run_feature_engineering(inp, out, preproc)


if __name__ == "__main__":
    main()
