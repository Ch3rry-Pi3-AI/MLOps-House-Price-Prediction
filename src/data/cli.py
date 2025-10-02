# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

import argparse
from .config import ProcessorConfig, load_yaml_config
from .processor import process_data


# -------------------------------------------------------------------
# Argument parsing
# -------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    """
    Parse command-line arguments for the data processing pipeline.

    Returns
    -------
    argparse.Namespace
        Parsed arguments with attributes: inp, out, cfg, policy, target.
    """
    p = argparse.ArgumentParser(description="House price data processing")
    p.add_argument("--in", dest="inp", required=True, help="Input CSV path")
    p.add_argument("--out", dest="out", required=True, help="Output CSV path")
    p.add_argument("--config", dest="cfg", help="YAML config (optional)")
    p.add_argument(
        "--policy", choices=["filter", "clip", "none"], help="Override outlier policy"
    )
    p.add_argument("--target", help="Override target column name")
    return p.parse_args()


# -------------------------------------------------------------------
# Main entry point
# -------------------------------------------------------------------

def main():
    """
    Execute the preprocessing pipeline from CLI arguments.

    - Loads config from YAML (if provided).
    - Allows overriding of outlier policy and target column.
    - Runs the process_data pipeline.
    """
    args = parse_args()
    cfg = load_yaml_config(args.cfg) if args.cfg else ProcessorConfig()

    # Override config from CLI flags if present
    if args.policy:
        cfg = ProcessorConfig(**{**cfg.__dict__, "outlier_policy": args.policy})
    if args.target:
        cfg = ProcessorConfig(**{**cfg.__dict__, "target": args.target})

    # Run pipeline
    process_data(args.inp, args.out, cfg)


if __name__ == "__main__":
    main()
