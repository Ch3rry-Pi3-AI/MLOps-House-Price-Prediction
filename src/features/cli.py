# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

import argparse
from .processor import run_feature_engineering


# -------------------------------------------------------------------
# Argument parsing
# -------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the feature engineering stage.

    Returns
    -------
    argparse.Namespace
        Parsed arguments with attributes: inp, out, preproc.
    """
    p = argparse.ArgumentParser(description="Feature engineering for housing data")
    p.add_argument("--input", dest="inp", required=True, help="Path to cleaned CSV file")
    p.add_argument("--output", dest="out", required=True, help="Path for output CSV file (engineered features)")
    p.add_argument("--preprocessor", dest="preproc", default="models/trained/preprocessor.pkl", help="Path for saving the preprocessor (default: models/trained/preprocessor.pkl)")
    return p.parse_args()


# -------------------------------------------------------------------
# Main entry point
# -------------------------------------------------------------------

def main():
    """
    Execute the feature engineering pipeline from CLI arguments.
    """
    args = parse_args()
    run_feature_engineering(args.inp, args.out, args.preproc)


if __name__ == "__main__":
    main()