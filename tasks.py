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
        Binary/command name, e.g., 'black' or 'ruff'.

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


# ====================================================================
# 🧱 FEATURE ENGINEERING
# ====================================================================

@task(
    help={
        "input":        "Path to CLEANED CSV (default: data/processed/cleaned_house_data.csv)",
        "output":       "Path for ENGINEERED CSV (default: data/processed/engineered_features.csv)",
        "preprocessor": "Path to save fitted preprocessor (default: models/trained/preprocessor.pkl)",
    }
)
def engineer(
    c,
    input: str = "data/processed/cleaned_house_data.csv",
    output: str = "data/processed/engineered_features.csv",
    preprocessor: str = "models/trained/preprocessor.pkl",
) -> None:
    """
    Run the feature engineering pipeline and write outputs.

    Steps
    -----
    1. Ensure common directories exist (data/, models/trained/).
    2. Call the feature pipeline orchestrator (`run_feature_engineering`).
    3. Save the engineered CSV and pickled preprocessor.

    Parameters
    ----------
    c : invoke.Context
        Invoke context.
    input : str, default="data/processed/cleaned_house_data.csv"
        Path to the CLEANED input CSV file.
    output : str, default="data/processed/engineered_features.csv"
        Path for the ENGINEERED CSV output.
    preprocessor : str, default="models/trained/preprocessor.pkl"
        Path for saving the fitted preprocessor (pickle).
    """
    _venv_notice()
    ensure_dirs(c)  # make sure directories exist

    # Lazy import: keep tasks lightweight unless the command is used
    from src.features.processor import run_feature_engineering

    print("⚙️  Running feature engineering...")
    df_trans = run_feature_engineering(input, output, preprocessor)
    print(f"✅ Engineered data saved to {output} (rows={len(df_trans)})")
    print(f"💾 Preprocessor saved to {preprocessor}")


@task(
    help={
        "k": "Only run tests matching expression (e.g., -k 'features and not slow')",
        "m": "Only run tests with marker (e.g., -m 'integration')",
    }
)
def features_test(c, k: str | None = None, m: str | None = None) -> None:
    """
    Run ONLY the feature engineering test suite.

    Parameters
    ----------
    c : invoke.Context
        Invoke context.
    k : str, optional
        Pytest -k expression to select feature tests.
    m : str, optional
        Pytest -m marker to select feature tests.
    """
    _venv_notice()
    target = "tests/features"
    cmd = f"pytest {PYTEST_DEFAULTS} {target}"
    if k:
        cmd += f' -k "{k}"'
    if m:
        cmd += f' -m "{m}"'
    _run(c, cmd)


@task(
    help={
        "input":        "Path to CLEANED CSV (default: data/processed/cleaned_house_data.csv)",
        "output":       "Path for ENGINEERED CSV (default: data/processed/engineered_features.csv)",
        "preprocessor": "Path to save fitted preprocessor (default: models/trained/preprocessor.pkl)",
        "skip_tests":   "Set true to skip running tests first (default: false)",
    }
)
def features(
    c,
    input: str = "data/processed/cleaned_house_data.csv",
    output: str = "data/processed/engineered_features.csv",
    preprocessor: str = "models/trained/preprocessor.pkl",
    skip_tests: bool | str = False,
) -> None:
    """
    Run feature-engineering *tests first*, then the pipeline.

    Steps
    -----
    1. (Optional) Run `tests/features` via pytest.
    2. Ensure directories exist.
    3. Run `engineer` task to build engineered features + preprocessor.

    Parameters
    ----------
    c : invoke.Context
        Invoke context.
    input : str, default="data/processed/cleaned_house_data.csv"
        Path to the CLEANED input CSV file.
    output : str, default="data/processed/engineered_features.csv"
        Path for the ENGINEERED CSV output.
    preprocessor : str, default="models/trained/preprocessor.pkl"
        Path for saving the fitted preprocessor (pickle).
    skip_tests : bool or str, default=False
        Whether to skip running the feature tests before the pipeline.
        Accepts common truthy/falsey strings.
    """
    _venv_notice()

    if not _to_bool(skip_tests):
        print("🧪 Running feature-engineering tests...")
        features_test(c)

    engineer(c, input=input, output=output, preprocessor=preprocessor)


# ====================================================================
# 🏋️ MODEL TRAINING
# ====================================================================

@task(
    help={
        "config": "Path to model training YAML (default: configs/model_config.yaml)",
        "data": "Path to ENGINEERED CSV (default: data/processed/engineered_features.csv)",
        "models_dir": "Directory to save trained model (default: models)",
        "mlflow_tracking_uri": "MLflow tracking URI (default: empty → file-based local store)",
    }
)
def train(
    c,
    config: str = "configs/model_config.yaml",
    data: str = "data/processed/engineered_features.csv",
    models_dir: str = "models",
    mlflow_tracking_uri: str = "",
) -> None:
    """
    Run the model training pipeline and register the model.

    Steps
    -----
    1. Ensure common directories exist (models/trained/).
    2. Call the training orchestrator (`run_training`).
    3. Persist the trained model locally and register in MLflow.

    Parameters
    ----------
    c : invoke.Context
        Invoke context.
    config : str, default="configs/model_config.yaml"
        Path to the model training YAML file.
    data : str, default="data/processed/engineered_features.csv"
        Path to the ENGINEERED input CSV file.
    models_dir : str, default="models"
        Directory where the trained model (.pkl) will be written under models/trained/.
    mlflow_tracking_uri : str, default=""
        MLflow tracking URI. Leave empty to use a local file-based store inside the run.
        Use http://localhost:5555 to log to your Docker MLflow server.
    """
    _venv_notice()
    ensure_dirs(c)  # make sure directories exist

    # Lazy import: keep tasks lightweight unless the command is used
    from src.models.processor import run_training

    # Determine tracking URI:
    # - If provided, use it as-is (e.g., http://localhost:5555).
    # - Otherwise, use a repo-local file store at <repo>/mlruns as a proper file:// URI.
    if mlflow_tracking_uri.strip():
        uri = mlflow_tracking_uri.strip()
    else:
        local_store = (REPO_ROOT / "mlruns").resolve()
        local_store.mkdir(parents=True, exist_ok=True)
        uri = local_store.as_uri()  # Windows-safe file:///C:/... URI

    print("⚙️  Running model training...")
    run_training(
        config_path=config,
        data_path=data,
        models_dir=models_dir,
        mlflow_tracking_uri=uri,
    )
    print(f"✅ Training complete. Model & run logged (models_dir={models_dir})")


@task(
    help={
        "k": "Only run tests matching expression (e.g., -k 'models and not slow')",
        "m": "Only run tests with marker (e.g., -m 'integration')",
    }
)
def models_test(c, k: str | None = None, m: str | None = None) -> None:
    """
    Run ONLY the model training test suite.

    Parameters
    ----------
    c : invoke.Context
        Invoke context.
    k : str, optional
        Pytest -k expression to select model tests.
    m : str, optional
        Pytest -m marker to select model tests.
    """
    _venv_notice()
    target = "tests/models"
    cmd = f"pytest {PYTEST_DEFAULTS} {target}"
    if k:
        cmd += f' -k "{k}"'
    if m:
        cmd += f' -m "{m}"'
    _run(c, cmd)


@task(
    help={
        "config": "Path to model training YAML (default: configs/model_config.yaml)",
        "data": "Path to ENGINEERED CSV (default: data/processed/engineered_features.csv)",
        "models_dir": "Directory to save trained model (default: models)",
        "mlflow_tracking_uri": "MLflow tracking URI (default: empty → file-based local store)",
        "skip_tests": "Set true to skip running model tests first (default: false)",
    }
)
def models(
    c,
    config: str = "configs/model_config.yaml",
    data: str = "data/processed/engineered_features.csv",
    models_dir: str = "models",
    mlflow_tracking_uri: str = "",
    skip_tests: bool | str = False,
) -> None:
    """
    Run model-training *tests first*, then the training pipeline.

    Steps
    -----
    1. (Optional) Run `tests/models` via pytest.
    2. Ensure directories exist.
    3. Run `train` task to fit and register the model.

    Parameters
    ----------
    c : invoke.Context
        Invoke context.
    config : str, default="configs/model_config.yaml"
        Path to the model training YAML file.
    data : str, default="data/processed/engineered_features.csv"
        Path to the ENGINEERED input CSV file.
    models_dir : str, default="models"
        Directory where the trained model (.pkl) will be written under models/trained/.
    mlflow_tracking_uri : str, default=""
        MLflow tracking URI. Leave empty to use a local file-based store inside the run.
        Use http://localhost:5555 to log to your Docker MLflow server.
    skip_tests : bool or str, default=False
        Whether to skip running the model tests before the pipeline.
        Accepts common truthy/falsey strings.
    """
    _venv_notice()

    if not _to_bool(skip_tests):
        print("🧪 Running model-training tests...")
        models_test(c)

    train(
        c,
        config=config,
        data=data,
        models_dir=models_dir,
        mlflow_tracking_uri=mlflow_tracking_uri,
    )

