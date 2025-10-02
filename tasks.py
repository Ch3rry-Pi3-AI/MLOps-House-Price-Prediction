# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------

from invoke import task
import sys
from pathlib import Path
from shutil import which
import shlex


# -------------------------------------------------------------------
# Platform & paths
# -------------------------------------------------------------------

# True on macOS/Linux, False on Windows
IS_POSIX: bool = sys.platform != "win32"

# Repo root (used for relative paths and globbing)
REPO_ROOT: Path = Path(__file__).parent.resolve()

# Ensure repo root is importable (so 'src/...' works inside tasks)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# -------------------------------------------------------------------
# Pytest / coverage defaults
# -------------------------------------------------------------------

PYTEST_DEFAULTS: str = "-q"
COV_DEFAULTS: str = "--cov=src --cov-report=term-missing"


# -------------------------------------------------------------------
# Internal helpers
# -------------------------------------------------------------------

def _venv_notice() -> None:
    """
    Print a heads-up if the user forgot to activate a virtual environment.

    Notes
    -----
    This does not block execution—it's a friendly reminder only.
    """
    if hasattr(sys, "base_prefix") and sys.prefix == sys.base_prefix:
        print("⚠️  You appear to be outside a virtual environment. Continue anyway...")


def _run(c, cmd: str, cwd: Path | None = None) -> None:
    """
    Run a shell command via Invoke, enabling PTY only where supported.

    Parameters
    ----------
    c : invoke.Context
        The Invoke context object.
    cmd : str
        The shell command to run.
    cwd : Path or None, optional
        Working directory to run the command from.
    """
    kwargs = {"pty": IS_POSIX}
    if cwd is not None:
        kwargs["cwd"] = str(cwd)
    print(f"→ {cmd}")
    c.run(cmd, **kwargs)


def _has_cmd(cmd: str) -> bool:
    """
    Check if a command is available on PATH.

    Parameters
    ----------
    cmd : str
        Binary/command name, e.g. 'black' or 'ruff'.

    Returns
    -------
    bool
        True if command exists on PATH, else False.
    """
    return which(cmd) is not None


# ====================================================================
# 🧪 TESTS & QUALITY
# ====================================================================

@task(
    help={
        "k": "Only run tests matching expression (e.g., -k 'cleaning and not slow')",
        "m": "Only run tests with marker (e.g., -m 'integration')",
        "path": "Path to run tests from (default: repo root / tests)",
    }
)
def test(c, k: str | None = None, m: str | None = None, path: str = "") -> None:
    """
    Run unit/integration tests with pytest.

    Parameters
    ----------
    c : invoke.Context
        Invoke context.
    k : str, optional
        Pytest -k expression to select tests.
    m : str, optional
        Pytest -m marker to select tests.
    path : str, default=""
        Path to run tests from (empty string runs default test discovery).
    """
    _venv_notice()
    target = path if path else ""
    cmd = f"pytest {PYTEST_DEFAULTS} {target}".strip()
    if k:
        cmd += f' -k "{k}"'
    if m:
        cmd += f' -m "{m}"'
    _run(c, cmd)


@task
def cov(c) -> None:
    """
    Run tests with coverage on src/.

    Parameters
    ----------
    c : invoke.Context
        Invoke context.
    """
    _venv_notice()
    _run(c, f"pytest {PYTEST_DEFAULTS} {COV_DEFAULTS}")


@task(optional=["path"])
def fmt(c, path: str = ".") -> None:
    """
    Format code with black if available.

    Parameters
    ----------
    c : invoke.Context
        Invoke context.
    path : str, default="."
        Target path to format.
    """
    _venv_notice()
    if _has_cmd("black"):
        _run(c, f"black {shlex.quote(path)}")
    else:
        print("black not installed. Skipping formatting.")


@task
def lint(c) -> None:
    """
    Lint code with ruff if available.

    Parameters
    ----------
    c : invoke.Context
        Invoke context.
    """
    _venv_notice()
    if _has_cmd("ruff"):
        _run(c, "ruff check .")
    else:
        print("ruff not installed. Skipping lint.")


@task
def clean(c) -> None:
    """
    Remove Python caches and build artefacts.

    Parameters
    ----------
    c : invoke.Context
        Invoke context.

    Notes
    -----
    Handles platform differences (Windows vs POSIX) for deletion commands.
    """
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


# ====================================================================
# 🧹 UTILS
# ====================================================================

@task
def ensure_dirs(c) -> None:
    """
    Create common project directories if missing.

    Parameters
    ----------
    c : invoke.Context
        Invoke context.
    """
    for d in [
        REPO_ROOT / "data" / "raw",
        REPO_ROOT / "data" / "processed",
        REPO_ROOT / "models" / "trained",
    ]:
        d.mkdir(parents=True, exist_ok=True)
        print(f"✅ Ensured: {d}")


# ====================================================================
# 🧼 PREPROCESSING
# ====================================================================

def _to_bool(val: str | bool) -> bool:
    """
    Convert common truthy/falsey strings to bool.

    Parameters
    ----------
    val : str or bool
        Value such as 'true', 'yes', '1', or a boolean.

    Returns
    -------
    bool
        Parsed boolean.
    """
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
    input: str = "data/raw/house_data.csv",
    output: str = "data/processed/cleaned_house_data.csv",
    policy: str = "filter",
    target: str = "price",
    iqr: float = 1.5,
    index: bool | str = False,
) -> None:
    """
    Run the preprocessing pipeline and write the processed CSV.

    Steps
    -----
    1. Build a ProcessorConfig from CLI flags.
    2. Call the pipeline orchestrator (`process_data`).
    3. Save to the provided output path and report row count.

    Parameters
    ----------
    c : invoke.Context
        Invoke context.
    input : str, default="data/raw/house_data.csv"
        Path to the input CSV file.
    output : str, default="data/processed/cleaned_house_data.csv"
        Path for the processed CSV output.
    policy : {"filter", "clip", "none"}, default="filter"
        Outlier handling strategy.
    target : str, default="price"
        Column used for outlier detection.
    iqr : float, default=1.5
        IQR multiplier for Tukey-style bounds.
    index : bool or str, default=False
        Whether to include the DataFrame index in the saved CSV.
        Accepts common truthy/falsey strings.

    Notes
    -----
    Imports project code lazily so `tasks.py` remains importable
    even when the project dependencies are not installed yet.
    """
    _venv_notice()

    # Lazy import: keep tasks lightweight unless the command is used
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
