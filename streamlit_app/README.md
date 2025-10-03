# **Streamlit App — House Price Prediction**

This folder contains a **Streamlit front-end** for the **MLOps House Price Prediction** project.
It provides a simple, interactive UI for sending requests to the **FastAPI backend** and displaying predictions in real time.

The app demonstrates how a user can interact with the trained model without touching the API directly.

## **Module Structure**

```
streamlit_app/
├── app.py             # Streamlit UI for inputs and results
└── requirements.txt   # Minimal dependencies for Streamlit + API calls
```

## **Features**

* Input form for:

  * Square footage (slider)
  * Bedrooms & bathrooms
  * Location (dropdown)
  * Year built (slider)
* **Predict Price** button sends a JSON request to the FastAPI service.
* Results include:

  * Predicted price (formatted as currency)
  * Confidence interval (±10% band by default)
  * Model metadata and latency
  * Top features (if returned by backend)
* Built-in **mock fallback** if the API cannot be reached.
* Footer shows **version, hostname, and IP** for debugging/demo purposes.

## **Running the App**

> Make sure the **FastAPI backend** is running (see `src/api/README.md`).

### Option A — With `uv`

```bash
uv pip install -r streamlit_app/requirements.txt
uv run streamlit run streamlit_app/app.py
```

### Option B — With plain `pip`

```bash
pip install -r streamlit_app/requirements.txt
streamlit run streamlit_app/app.py
```

## **Connecting to the API**

* By default, the app looks for the backend at:

  ```
  http://127.0.0.1:8000
  ```
* You can override this by setting an environment variable:

  ```bash
  export API_URL="http://localhost:8000"
  ```

## ✅ Summary

The **Streamlit app** provides a lightweight, interactive UI for testing and demoing the house-price prediction model.

It pairs with the **FastAPI backend** to form a complete **model serving + user interface** pipeline:

* **API** → scalable prediction service
* **Streamlit** → human-friendly interface for business/demo users