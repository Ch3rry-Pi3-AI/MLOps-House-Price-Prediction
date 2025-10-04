# -------------------------------------------------------------------
# app.py — Streamlit UI for House Price Prediction
# -------------------------------------------------------------------
from __future__ import annotations

import os
import socket
import time
from typing import Dict, List, Tuple

import requests
import streamlit as st


# -------------------------------------------------------------------
# Page Config
# -------------------------------------------------------------------
st.set_page_config(
    page_title="House Price Predictor",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------------------------------------------------------
# Constants & Helpers
# -------------------------------------------------------------------
DEFAULT_API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_MODEL = os.getenv("APP_MODEL", "XGBoost")  # purely cosmetic fallback label

# Keep UI choices aligned with training-time categories if applicable
LOCATION_OPTIONS_UI = ["Urban", "Suburban", "Rural"]  # title-cased for display
LOCATION_OPTIONS_PAYLOAD = [opt.lower() for opt in LOCATION_OPTIONS_UI]


def call_predict(api_url: str, payload: Dict) -> Dict:
    """
    Call the FastAPI /predict endpoint.

    Parameters
    ----------
    api_url : str
        Base URL of the FastAPI service (e.g., http://127.0.0.1:8000).
    payload : dict
        JSON-serialisable payload matching HousePredictionRequest.

    Returns
    -------
    dict
        Parsed JSON response from the API.

    Raises
    ------
    requests.exceptions.RequestException
        If the request fails or returns a non-2xx status.
    """
    predict_url = f"{api_url.rstrip('/')}/predict"
    r = requests.post(predict_url, json=payload, timeout=20)
    r.raise_for_status()
    return r.json()


def hostname_ip() -> Tuple[str, str]:
    """Return (hostname, ip) for footer display."""
    host = socket.gethostname()
    try:
        ip = socket.gethostbyname(host)
    except Exception:
        ip = "N/A"
    return host, ip


def pick_model_name(pred: Dict, default_env_model: str) -> str:
    """
    Choose the model name to display.
    Priority: API payload ('model'/'model_name') -> APP_MODEL env -> 'Unknown'.
    """
    return str(
        pred.get("model")
        or pred.get("model_name")
        or default_env_model
        or "Unknown"
    )


def extract_feature_importance(pred: Dict) -> Dict[str, float]:
    """
    Robustly extract a name->score mapping for feature importances from the API payload.

    Supported shapes:
      - {"features_importance": {"sqft": 0.4, "bathrooms": 0.2, ...}}
      - {"feature_importance": {...}} / {"feature_importances": {...}}
      - {"top_features": [{"name": "sqft", "importance": 0.4}, ...]}
      - {"top_factors": [{"feature": "sqft", "score": 0.4}, ...]}
      - {"features_importance": [["sqft", 0.4], ["bathrooms", 0.2], ...]}
    """
    candidates = [
        "features_importance",
        "feature_importance",
        "feature_importances",
        "top_features",
        "top_factors",
    ]
    data = None
    for key in candidates:
        if key in pred:
            data = pred[key]
            break

    if not data:
        return {}

    # If it's already a dict: {name: score}
    if isinstance(data, dict):
        out = {}
        for k, v in data.items():
            try:
                out[str(k)] = float(v)
            except (TypeError, ValueError):
                continue
        return out

    # If it's a list of [name, score]
    if isinstance(data, list) and data and isinstance(data[0], (list, tuple)) and len(data[0]) == 2:
        out = {}
        for k, v in data:
            try:
                out[str(k)] = float(v)
            except (TypeError, ValueError):
                continue
        return out

    # If it's a list of dicts like {"name": "...", "importance": 0.4} or {"feature": "...", "score": 0.4}
    if isinstance(data, list) and data and isinstance(data[0], dict):
        out = {}
        for item in data:
            name = item.get("name") or item.get("feature") or item.get("key")
            val = item.get("importance") or item.get("score") or item.get("value")
            if name is None or val is None:
                continue
            try:
                out[str(name)] = float(val)
            except (TypeError, ValueError):
                continue
        return out

    return {}


# --------- Pretty-printing for feature names (for Top Factors) ---------
def _title_case_words(s: str) -> str:
    """Title-case words but keep common lowercase joiners readable."""
    words = s.split()
    joiners = {"and", "or", "of", "per", "vs", "for", "to", "in"}
    if not words:
        return s
    out = [words[0].capitalize()]
    for w in words[1:]:
        out.append(w if w.lower() in joiners else w.capitalize())
    return " ".join(out)


def pretty_feature_name(raw: str) -> str:
    """
    Convert model/transformer feature names into a user-friendly label.

    Handles patterns like:
      - "num__house_age"              -> "House age"
      - "num__price_per_sqft"         -> "Price per sqft"
      - "num__bed_bath_ratio"         -> "Bed/Bath ratio"
      - "num__sqft"                   -> "Square footage"
      - "cat__location_Waterfront"    -> "Location: Waterfront"
      - "cat__location_Urban"         -> "Location: Urban"
      - "bedrooms" / "bathrooms"      -> "Bedrooms" / "Bathrooms"
    """
    s = str(raw)

    # Strip common prefixes from ColumnTransformer pipelines
    for prefix in ("num__", "cat__", "bin__", "ohe__", "tfidf__", "scale__", "std__", "minmax__"):
        if s.startswith(prefix):
            s = s[len(prefix):]

    # If it's a one-hot expansion like 'location_Waterfront'
    if "__" in s:
        # Sometimes transformers keep double underscores; replace them
        s = s.replace("__", "_")

    if "_" in s and s.split("_", 1)[0] in {"location", "loc", "city", "region"}:
        head, tail = s.split("_", 1)
        head = head.capitalize()
        tail = tail.replace("_", " ")
        return f"{head}: {_title_case_words(tail)}"

    # Known mappings for engineered/base features
    known = {
        "sqft": "Square footage",
        "house_age": "House age",
        "price_per_sqft": "Price per sqft",
        "bed_bath_ratio": "Bed/Bath ratio",
        "year_built": "Year built",
        "bedrooms": "Bedrooms",
        "bathrooms": "Bathrooms",
        "location": "Location",
        "condition": "Condition",
    }
    if s in known:
        return known[s]

    # Fallback: replace underscores with spaces and title-case
    s = s.replace("_", " ")
    return _title_case_words(s)


# -------------------------------------------------------------------
# Header
# -------------------------------------------------------------------
st.title("House Price Prediction")
st.markdown(
    """
    <p style="font-size: 18px; color: gray; margin-top: -8px;">
        A simple MLOps demonstration project for real-time house price prediction
    </p>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------------------
# Layout
# -------------------------------------------------------------------
col1, col2 = st.columns(2, gap="large")

# ---------------------- Left Column: Form ---------------------------
with col1:
    st.markdown("### Input")
    with st.container(border=True):
        sqft = st.slider("Square Footage", min_value=500, max_value=5000, value=1500, step=50)
        c1, c2 = st.columns(2)
        with c1:
            bedrooms = st.selectbox("Bedrooms", options=[1, 2, 3, 4, 5, 6], index=2)
        with c2:
            bathrooms = st.selectbox("Bathrooms", options=[1, 1.5, 2, 2.5, 3, 3.5, 4], index=2)

        st.caption("Location")
        location_ui = st.selectbox("", options=LOCATION_OPTIONS_UI, index=1, label_visibility="collapsed")
        location_payload = location_ui.lower()

        # NOTE: backend schema allows up to 2023; keep UI consistent to avoid validation errors.
        year_built = st.slider("Year Built", min_value=1900, max_value=2023, value=2000, step=1)

        # Future enhancement: expose condition if your model uses it as categorical
        condition = "Good"

        predict_button = st.button("Predict Price", use_container_width=True)

# --------------------- Right Column: Results ------------------------
with col2:
    st.markdown("### Prediction Results")
    with st.container(border=True):
        if predict_button:
            payload = {
                "sqft": float(sqft),
                "bedrooms": int(bedrooms),
                "bathrooms": float(bathrooms),
                "location": location_payload,
                "year_built": int(year_built),
                "condition": condition,
            }

            st.write(f"Connecting to API at: `{DEFAULT_API_URL.rstrip('/')}/predict`")
            start = time.perf_counter()
            try:
                with st.spinner("Calculating prediction..."):
                    result = call_predict(DEFAULT_API_URL, payload)
                elapsed = time.perf_counter() - start
                # Persist in session for re-render
                st.session_state.prediction = result
                st.session_state.prediction_elapsed = elapsed
            except requests.exceptions.RequestException as e:
                st.error(f"Error connecting to API: {e}")
                st.warning("Using mock data for demonstration purposes. Please check your API connection.")
                # Mock fallback (demo only) — include keys to exercise UI paths
                st.session_state.prediction = {
                    "predicted_price": 467145,
                    "confidence_interval": [420430.5, 513859.5],
                    "features_importance": {
                        "num__house_age": 0.53,
                        "num__sqft": 0.28,
                        "num__price_per_sqft": 0.17,
                        "cat__location_Waterfront": 0.01,
                        "num__bed_bath_ratio": 0.00,
                    },
                    "prediction_time": "mock",
                    "prediction_duration": 0.18,
                    "model": "XGBoost (mock)",
                }
                st.session_state.prediction_elapsed = time.perf_counter() - start

        # Render last prediction if available
        if "prediction" in st.session_state:
            pred: Dict = st.session_state.prediction
            elapsed_s: float = float(st.session_state.get("prediction_elapsed", 0.0))

            # Main value
            price_val = float(pred.get("predicted_price", 0.0))
            formatted_price = "${:,.0f}".format(price_val)
            st.markdown(
                f"""
                <div style="font-size: 42px; font-weight: 700; margin: 6px 0 14px 0;">
                    {formatted_price}
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Info cards
            a, b = st.columns(2)
            with a:
                st.markdown("##### Price Range")
                ci = pred.get("confidence_interval", [None, None])
                if isinstance(ci, list) and len(ci) == 2 and all(v is not None for v in ci):
                    lower = "${:,.1f}".format(float(ci[0]))
                    upper = "${:,.1f}".format(float(ci[1]))
                    st.metric(label="Confidence Band (±10%)", value=f"{lower}  →  {upper}")
                else:
                    st.write("—")

            with b:
                st.markdown("##### Prediction Details")
                # Prefer API-provided prediction_duration (seconds); fallback to API's prediction_time if numeric; else measured elapsed
                api_duration = pred.get("prediction_duration")
                api_time_val = pred.get("prediction_time")
                pred_time_s = None
                # Try duration first
                try:
                    if api_duration is not None:
                        pred_time_s = float(api_duration)
                except (TypeError, ValueError):
                    pred_time_s = None
                # If duration not available, accept numeric/string numeric prediction_time
                if pred_time_s is None:
                    try:
                        if api_time_val is not None and isinstance(api_time_val, (int, float, str)):
                            pred_time_s = float(api_time_val)  # only works if API gave seconds as number/string
                    except (TypeError, ValueError):
                        pred_time_s = None
                # Final fallback to measured elapsed
                if pred_time_s is None:
                    pred_time_s = elapsed_s

                st.metric(label="Prediction time (s)", value=f"{pred_time_s:.2f}")

                # Prefer API model name, fallback to APP_MODEL env
                model_label = pick_model_name(pred, APP_MODEL)
                st.caption(f"Model: **{model_label}**")

            # Top factors (Top 3, numbered, pretty names)
            st.markdown("#### Top Factors")
            fi: Dict[str, float] = extract_feature_importance(pred)
            if fi:
                items = sorted(fi.items(), key=lambda kv: kv[1], reverse=True)[:3]
                # Create a numbered list with bold labels and aligned scores
                lines = []
                for idx, (name, score) in enumerate(items, start=1):
                    pretty = pretty_feature_name(name)
                    lines.append(f"{idx}. **{pretty}** — {score:.2f}")
                st.markdown("\n".join([f"- {ln}" for ln in lines]))
            else:
                st.write("No feature importance provided by the backend.")

        else:
            st.markdown(
                """
                <div style="display: flex; height: 280px; align-items: center; justify-content: center; color: #6b7280; text-align: center;">
                    Fill out the form and click <strong>Predict Price</strong> to see the estimated house price.
                </div>
                """,
                unsafe_allow_html=True,
            )

# -------------------------------------------------------------------
# Footer
# -------------------------------------------------------------------
host, ip = hostname_ip()
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div style="text-align: center; color: gray; margin-top: 6px;">
        <p><strong>Built for MLOps 'Pimp My Portfolio' course</strong></p>
        <p>by <a href="https://www.linkedin.com/in/roger-j-campbell-1a33771ab/" target="_blank">Ch3rry Pi3 AI</a></p>
        <p><strong>Version:</strong> {APP_VERSION} &nbsp;|&nbsp; <strong>Hostname:</strong> {host} &nbsp;|&nbsp; <strong>IP:</strong> {ip}</p>
    </div>
    """,
    unsafe_allow_html=True,
)