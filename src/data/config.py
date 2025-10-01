from dataclasses import dataclass
from typing import Literal, Optional

OutlierPolicy = Literal["filter", "clip", "none"]


@dataclass(frozen=True)
class ProcessorConfig:
    target: str = "price"
    outlier_policy: OutlierPolicy = "filter"  # "filter" | "clip" | "none"
    iqr_multiplier: float = 1.5  # whisker width
    save_index: bool = False  # when writing CSV


# (Optional) YAML loader if you want configs in pyyaml
def load_yaml_config(path: str) -> ProcessorConfig:
    import yaml

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    return ProcessorConfig(**data)
