# tasks.py
from invoke import task
import sys
from pathlib import Path
from shutil import which
import shlex

# ---------- Platform & paths ----------
IS_POSIX = sys.platform != "win32"  # True on macOS/Linux, False on Windows
REPO_ROOT = Path(__file__).parent.resolve()

# Ensure repo root is importable (so 'src/...' works inside tasks)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# ---------- Pytest defaults ----------
PYTEST_DEFAULTS = "-q"
COV_DEFAULTS = "--cov=src --cov-report=term-missing"


def _venv_notice():
    """Heads-up if user forgot to activate venv."""
    if hasattr(sys, "base_prefix") and sys.prefix == sys.base_prefix:
        print("⚠️  You appear to be outside a virtual environment. Continue anyway...")


def _run(c, cmd: str, cwd: Path | None = None):
    """Run shell commands with POSIX pty only where supported."""
    kwargs = {"pty": IS_POSIX}
    if cwd is not None:
        kwargs["cwd"] = str(cwd)
    print(f"→ {cmd}")
    c.run(cmd, **kwargs)


def _has_cmd(cmd: str) -> bool:
    return which(cmd) is not None


# =====================================================================
# 🧪 TESTS & QUALITY
# =====================================================================

@task(
    help={
        "k": "Only run tests matching expression (e.g., -k 'cleaning and not slow')",
        "m": "Only run tests with marker (e.g., -m 'integration')",
        "path": "Path to run tests from (default: repo root / tests)",
    }
)
def test(c, k=None, m=None, path=""):
    """Run unit/integration tests with pytest."""
    _venv_notice()
    target = path if path else ""
    cmd = f"pytest {PYTEST_DEFAULTS} {target}".strip()
    if k:
        cmd += f' -k "{k}"'
    if m:
        cmd += f' -m "{m}"'
    _run(c, cmd)


@task
def cov(c):
    """Run tests with coverage on src/."""
    _venv_notice()
    _run(c, f"pytest {PYTEST_DEFAULTS} {COV_DEFAULTS}")


@task(optional=["path"])
def fmt(c, path="."):
    """Format code with black if available."""
    _venv_notice()
    if _has_cmd("black"):
        _run(c, f"black {shlex.quote(path)}")
    else:
        print("black not installed. Skipping formatting.")


@task
def lint(c):
    """Lint code with ruff if available."""
    _venv_notice()
    if _has_cmd("ruff"):
        _run(c, "ruff check .")
    else:
        print("ruff not installed. Skipping lint.")


@task
def clean(c):
    """Remove Python caches and build artefacts."""
    _venv_notice()
    patterns = [
        "**/__pycache__", "**/*.pyc", "**/*.pyo",
        ".pytest_cache", ".ruff_cache", "dist", "build", "*.egg-info",
        ".coverage", "htmlcov",
    ]
    for p in patterns:
        for path in REPO_ROOT.glob(p):
            if path.is_dir():
                _run(c, f'rmdir /S /Q "{path}"' if not IS_POSIX else f'rm -rf "{path}"')
            else:
                _run(c, f'del /Q "{path}"' if not IS_POSIX else f'rm -f "{path}"')


# =====================================================================
# 🧹 UTILS
# =====================================================================

@task
def ensure_dirs(c):
    """Create common project directories if missing."""
    for d in [
        REPO_ROOT / "data" / "raw",
        REPO_ROOT / "data" / "processed",
        REPO_ROOT / "models" / "trained"
    ]:
        d.mkdir(parents=True, exist_ok=True)
        print(f"✅ Ensured: {d}")


# =====================================================================
# 🧼 PREPROCESSING
# =====================================================================

def _to_bool(val: str | bool) -> bool:
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in {"1", "true", "yes", "y", "on"}

@task(
    help={
        "input":  "Path to raw CSV (default: data/raw/house_data.csv)",
        "output": "Path for processed CSV (default: data/processed/cleaned_house_data.csv)",
        "policy": "Outlier policy: filter | clip | none (default: filter)",
        "target": "Target column used for outlier handling (default: price)",
        "iqr":    "IQR multiplier for outlier bounds (default: 1.5)",
        "index":  "Save index to CSV (true/false, default: false)",
    }
)
def preprocess(
    c,
    input="data/raw/house_data.csv",
    output="data/processed/cleaned_house_data.csv",
    policy="filter",
    target="price",
    iqr=1.5,
    index=False,
):
    """Run the preprocessing pipeline and write the processed CSV."""
    _venv_notice()
    # Lazy import so tasks.py doesn't import project code unless needed
    from src.data.processor import process_data
    from src.data.config import ProcessorConfig

    cfg = ProcessorConfig(
        target=target,
        outlier_policy=policy,
        iqr_multiplier=float(iqr),
        save_index=_to_bool(index),
    )
    print(f"⚙️  Preprocessing with config: {cfg}")
    processed = process_data(input, output, cfg)
    print(f"✅ Preprocessed data saved to {output} (rows={len(processed)})")