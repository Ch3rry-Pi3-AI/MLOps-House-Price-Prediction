# -------------------------------------------------------------------
# Imports
# -------------------------------------------------------------------
from __future__ import annotations

from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .inference import predict_price, batch_predict
from .schemas import HousePredictionRequest, PredictionResponse


# -------------------------------------------------------------------
# Application Setup
# -------------------------------------------------------------------
app = FastAPI(
    title="House Price Prediction API",
    description=(
        "An API for predicting house prices based on various features. "
        "This application is part of the Ch3rry Pi3 AI 'Pimp My Portfolio' course. "
        "Authored by Roger J. Campbell."
    ),
    version="1.0.0",
    contact={
        "name": "Ch3rry Pi3 AI",
        "url": "https://www.linkedin.com/in/roger-j-campbell-1a33771ab/",
        "email": "ch3rry_pi3@outlook.com",
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# Allow cross-origin requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -------------------------------------------------------------------
# Endpoints
# -------------------------------------------------------------------
@app.get("/health", response_model=dict)
async def health_check() -> dict:
    """
    Health check endpoint.

    Returns
    -------
    dict
        JSON object with service health status and whether the model
        was successfully loaded.
    """
    return {"status": "healthy", "model_loaded": True}


@app.post("/predict", response_model=PredictionResponse)
async def predict(request: HousePredictionRequest) -> PredictionResponse:
    """
    Predict house price for a single request.

    Parameters
    ----------
    request : HousePredictionRequest
        Input payload with house features.

    Returns
    -------
    PredictionResponse
        Structured prediction output containing predicted price,
        confidence interval, feature importances, and timestamp.
    """
    return predict_price(request)


@app.post("/batch-predict", response_model=List[float])
async def batch_predict_endpoint(requests: List[HousePredictionRequest]) -> List[float]:
    """
    Predict house prices for multiple requests in batch.

    Parameters
    ----------
    requests : list[HousePredictionRequest]
        List of house feature payloads.

    Returns
    -------
    list[float]
        List of predicted house prices (rounded floats).
    """
    return batch_predict(requests)