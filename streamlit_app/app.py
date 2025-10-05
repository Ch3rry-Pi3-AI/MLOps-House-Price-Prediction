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
# Page Configuration
# -------------------------------------------------------------------
st.set_page_config(
    page_title="🏠 House Price Predictor",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# (Aesthetics notes)
# - Keep a consistent accent colour (e.g., #2563EB for headings/KPIs).
# - Emojis to consider:
#   Inputs: 📐 🛌 🛁 📍 📅
#   Actions/Status: 🚀 ⏳ ✅ ⚠️
#   Results/Viz: 📊 📈 🧠
# - Use st.divider() to separate major sections for visual rhythm.


# -------------------------------------------------------------------
# Constants & Helpers
# -------------------------------------------------------------------
DEFAULT_API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_MODEL = os.getenv("APP_MODEL", "XGBoost")

# Location dropdown options
LOCATION_OPTIONS_UI = ["Urban", "Suburban", "Rural"]
LOCATION_OPTIONS_PAYLOAD = [opt.lower() for opt in LOCATION_OPTIONS_UI]


# -------------------------------------------------------------------
# API Communication
# -------------------------------------------------------------------
def call_predict(api_url: str, payload: Dict) -> Dict:
    """Send payload to FastAPI `/predict` endpoint and return JSON response."""
    predict_url = f"{api_url.rstrip('/')}/predict"
    r = requests.post(predict_url, json=payload, timeout=20)
    r.raise_for_status()
    return r.json()


# -------------------------------------------------------------------
# System Information Helpers
# -------------------------------------------------------------------
def hostname_ip() -> Tuple[str, str]:
    """Return current hostname and IP address for footer display."""
    host = socket.gethostname()
    try:
        ip = socket.gethostbyname(host)
    except Exception:
        ip = "N/A"
    return host, ip


# -------------------------------------------------------------------
# Result Parsing Utilities
# -------------------------------------------------------------------
def pick_model_name(pred: Dict, default_env_model: str) -> str:
    """Select model name from response or fallback to environment variable."""
    return str(
        pred.get("model")
        or pred.get("model_name")
        or default_env_model
        or "Unknown"
    )


def extract_feature_importance(pred: Dict) -> Dict[str, float]:
    """Extract feature importance mapping (feature → score) from API response."""
    candidates = [
        "features_importance",
        "feature_importance",
        "feature_importances",
        "top_features",
        "top_factors",
    ]
    data = next((pred[k] for k in candidates if k in pred), None)
    if not data:
        return {}

    if isinstance(data, dict):
        return {str(k): float(v) for k, v in data.items() if isinstance(v, (int, float))}

    if isinstance(data, list) and data and isinstance(data[0], (list, tuple)):
        return {str(k): float(v) for k, v in data if isinstance(v, (int, float))}

    if isinstance(data, list) and data and isinstance(data[0], dict):
        out = {}
        for item in data:
            name = item.get("name") or item.get("feature")
            val = item.get("importance") or item.get("score") or item.get("value")
            if name is not None and val is not None:
                try:
                    out[str(name)] = float(val)
                except (TypeError, ValueError):
                    continue
        return out
    return {}


# -------------------------------------------------------------------
# Feature Name Formatting
# -------------------------------------------------------------------
def _title_case_words(s: str) -> str:
    """Title-case words but preserve readability for short joiners."""
    words = s.split()
    joiners = {"and", "or", "of", "per", "vs", "for", "to", "in"}
    if not words:
        return s
    out = [words[0].capitalize()]
    for w in words[1:]:
        out.append(w if w.lower() in joiners else w.capitalize())
    return " ".join(out)


def pretty_feature_name(raw: str) -> str:
    """Convert model feature names into readable labels for UI display."""
    s = str(raw)
    for prefix in ("num__", "cat__", "bin__", "ohe__", "tfidf__", "scale__", "std__", "minmax__"):
        if s.startswith(prefix):
            s = s[len(prefix):]
    s = s.replace("__", "_")

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
    return _title_case_words(s.replace("_", " "))


# -------------------------------------------------------------------
# UI: Header (centred)
# -------------------------------------------------------------------
st.markdown(
    "<h1 style='font-size:42px; text-align:center; margin-bottom:0;'>🏡 House Price Prediction</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    """
    <p style="font-size:18px; color:gray; margin-top:6px; text-align:center;">
        End-2-End <strong>MLOps</strong> project for the <em>'Pimp My Portfolio'</em> course.
    </p>
    """,
    unsafe_allow_html=True,
)
st.divider()


# -------------------------------------------------------------------
# UI Layout — Two Columns
# -------------------------------------------------------------------
col1, col2 = st.columns(2, gap="large")


# -------------------------------------------------------------------
# Left Column — Input Form
# -------------------------------------------------------------------
with col1:
    st.subheader("🧾 Input Parameters")
    st.markdown("<small>Adjust the sliders or selectors, then click <strong>Predict Price</strong>.</small>", unsafe_allow_html=True)

    with st.container(border=True):
        sqft = st.slider("📐 Square Footage", 500, 5000, 1500, 50)

        c1, c2 = st.columns(2)
        with c1:
            bedrooms = st.selectbox("🛌 Bedrooms", [1, 2, 3, 4, 5, 6], index=2)
        with c2:
            bathrooms = st.selectbox("🛁 Bathrooms", [1, 1.5, 2, 2.5, 3, 3.5, 4], index=2)

        st.caption("📍 Location")
        location_ui = st.selectbox("", LOCATION_OPTIONS_UI, index=1, label_visibility="collapsed")
        location_payload = location_ui.lower()

        year_built = st.slider("📅 Year Built", 1900, 2023, 2000, 1)
        condition = "Good"

        st.markdown("<br>", unsafe_allow_html=True)
        predict_button = st.button("🚀 Predict Price", use_container_width=True)


# -------------------------------------------------------------------
# Right Column — Results Panel
# -------------------------------------------------------------------
with col2:
    st.subheader("🧠 Prediction Results")
    # NEW: Subheading under the results header (like the input side)
    st.markdown(
        "<small>After submitting, view the estimate, price range, model used, and runtime here.</small>",
        unsafe_allow_html=True,
    )

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

            st.markdown(f"Connecting to API: `{DEFAULT_API_URL.rstrip('/')}/predict`")

            start = time.perf_counter()
            try:
                with st.spinner("⏳ Calculating prediction..."):
                    result = call_predict(DEFAULT_API_URL, payload)
                elapsed = time.perf_counter() - start
                st.session_state.prediction = result
                st.session_state.prediction_elapsed = elapsed
                st.session_state.payload = payload  # ✅ Store payload for later tabs

            except requests.exceptions.RequestException as e:
                st.error(f"⚠️ API connection error: {e}")
                st.warning("Using mock data for demonstration only.")
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
                    "prediction_duration": 0.18,
                    "model": "XGBoost (mock)",
                }
                st.session_state.prediction_elapsed = time.perf_counter() - start
                st.session_state.payload = payload

        if "prediction" in st.session_state:
            pred = st.session_state.prediction
            elapsed_s = float(st.session_state.get("prediction_elapsed", 0.0))
            payload_safe = st.session_state.get("payload", {})  # ✅ safe access

            # --- Main prediction (headline) ---
            price_val = float(pred.get("predicted_price", 0.0))
            formatted_price = f"£{price_val:,.0f}"
            st.markdown(
                f"<h2 style='font-weight:700;color:#2563eb;margin:10px 0;'>{formatted_price}</h2>",
                unsafe_allow_html=True,
            )

            # --- Compact KPI row (replaces large st.metric cards) ---
            def _stat_chip(label: str, value: str) -> str:
                return f"""
                <div style="
                    border:1px solid #374151;
                    background:#0b1220;
                    border-radius:12px;
                    padding:10px 12px;
                    margin-top:6px;">
                    <div style="font-size:12px;color:#9ca3af;letter-spacing:.04em;text-transform:uppercase;">
                        {label}
                    </div>
                    <div style="font-size:18px;font-weight:600;line-height:1.2;">
                        {value}
                    </div>
                </div>
                """

            k1, k2, k3 = st.columns(3)
            ci = pred.get("confidence_interval", [None, None])
            with k1:
                if isinstance(ci, list) and len(ci) == 2:
                    ci_text = f"£{ci[0]:,.0f} – £{ci[1]:,.0f}"
                else:
                    ci_text = "—"
                st.markdown(_stat_chip("Price Range", ci_text), unsafe_allow_html=True)

            with k2:
                model_label = pick_model_name(pred, APP_MODEL)
                st.markdown(_stat_chip("Model", model_label), unsafe_allow_html=True)

            with k3:
                pred_time_s = float(pred.get("prediction_duration", elapsed_s))
                st.markdown(_stat_chip("Prediction Time (s)", f"{pred_time_s:.2f}"), unsafe_allow_html=True)

            # --- Tabs for details ---
            summary_tab, factors_tab, payload_tab = st.tabs(["📊 Summary", "📈 Top Factors", "📦 Payload"])

            with summary_tab:
                st.markdown(
                    f"""
                    <div style="font-size:16px;line-height:1.6;">
                        <strong>Estimated Price:</strong> {formatted_price}<br/>
                        <strong>Model:</strong> {model_label}<br/>
                        <strong>Confidence Interval:</strong>
                        {f"£{ci[0]:,.0f} – £{ci[1]:,.0f}" if ci and len(ci)==2 else "—"}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            with factors_tab:
                fi = extract_feature_importance(pred)
                if not fi:
                    st.caption("No feature importance provided by the backend.")
                else:
                    st.markdown("#### Top 3 Factors Influencing Price")
                    items = sorted(fi.items(), key=lambda kv: kv[1], reverse=True)[:3]
                    formatted = [
                        f"<li><strong>{pretty_feature_name(k)}</strong> — {v:.2f}</li>"
                        for k, v in items
                    ]
                    st.markdown(
                        "<ol style='line-height:1.8;margin-top:0;'>"
                        + "".join(formatted)
                        + "</ol>",
                        unsafe_allow_html=True,
                    )

            with payload_tab:
                st.caption("Request payload sent to API")
                st.json(payload_safe)  # ✅ Fixed reference
                if "error" not in pred:
                    with st.expander("Raw API response"):
                        st.json(pred)

        else:
            st.markdown(
                """
                <div style="display:flex;height:250px;align-items:center;justify-content:center;color:#6b7280;text-align:center;">
                    Fill out the form and click <strong>Predict Price</strong> to see your result.
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
    <div style="text-align:center;color:gray;margin-top:6px;">
        <p><strong>Built for MLOps 'Pimp My Portfolio' course</strong></p>
        <p>by <a href="https://www.linkedin.com/in/roger-j-campbell-1a33771ab/" target="_blank">Ch3rry Pi3 AI</a></p>
        <p><strong>Version:</strong> {APP_VERSION} &nbsp;|&nbsp; <strong>Host:</strong> {host} &nbsp;|&nbsp; <strong>IP:</strong> {ip}</p>
    </div>
    """,
    unsafe_allow_html=True,
)
