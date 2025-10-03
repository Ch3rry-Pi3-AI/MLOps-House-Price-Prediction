# -------------------------------------------------------------------
# app.py — Streamlit UI for House Price Prediction
# -------------------------------------------------------------------
from __future__ import annotations

import json
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
APP_MODEL = os.getenv("APP_MODEL", "XGBoost")  # purely cosmetic label

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
                # Mock fallback (demo only)
                st.session_state.prediction = {
                    "predicted_price": 467145,
                    "confidence_interval": [420430.5, 513859.5],
                    "features_importance": {"sqft": 0.43, "location": 0.27, "bathrooms": 0.15},
                    "prediction_time": "mock",
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
                st.markdown("##### Inference Details")
                st.metric(label="Latency (s)", value=f"{elapsed_s:.2f}")
                st.caption(f"Model: **{APP_MODEL}**")

            # Top factors (if available)
            fi: Dict[str, float] = pred.get("features_importance", {}) or {}
            st.markdown("#### Top Factors")
            if fi:
                # sort by importance desc and show top 5
                items = sorted(fi.items(), key=lambda kv: kv[1], reverse=True)[:5]
                for name, score in items:
                    st.write(f"- **{name}** — {score:.2f}")
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