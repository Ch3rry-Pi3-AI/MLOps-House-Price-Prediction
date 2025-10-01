import argparse
from .config import ProcessorConfig, load_yaml_config
from .processor import process_data


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="House price data processing")
    p.add_argument("--in", dest="inp", required=True, help="Input CSV path")
    p.add_argument("--out", dest="out", required=True, help="Output CSV path")
    p.add_argument("--config", dest="cfg", help="YAML config (optional)")
    p.add_argument(
        "--policy", choices=["filter", "clip", "none"], help="Override outlier policy"
    )
    p.add_argument("--target", help="Override target column name")
    return p.parse_args()


def main():
    args = parse_args()
    cfg = load_yaml_config(args.cfg) if args.cfg else ProcessorConfig()
    if args.policy:
        cfg = ProcessorConfig(**{**cfg.__dict__, "outlier_policy": args.policy})
    if args.target:
        cfg = ProcessorConfig(**{**cfg.__dict__, "target": args.target})
    process_data(args.inp, args.out, cfg)


if __name__ == "__main__":
    main()
