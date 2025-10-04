Perfect 👌 — here’s the next stage’s **README**, adapted for your **deployment branch**.
It keeps the same professional tone and structure as your earlier stages while introducing Docker, FastAPI, Streamlit, and Docker Compose integration.



# **Model Deployment Stage**

This branch extends the **MLOps House Price Prediction** project by implementing the **model deployment pipeline**.
It introduces a full deployment stack built with **FastAPI** (for inference) and **Streamlit** (for the UI), both containerised using **Docker**, and orchestrated together with **Docker Compose**.

This stage completes the MLOps lifecycle — transforming trained models and preprocessing pipelines into live, user-facing services that can be built, run, and published anywhere.



## **Project Structure**

```
mlops-house-price-prediction/
├── .venv/
├── .github/
├── data/
├── models/
├── notebooks/
├── src/
│   ├── api/                                # 🚀 NEW: FastAPI inference service
│   │   ├── __init__.py
│   │   ├── inference.py                    #   Loads model + preprocessor, defines predict()
│   │   ├── main.py                         #   FastAPI entrypoint and routing
│   │   ├── schemas.py                      #   Pydantic request/response models
│   │   └── requirements.txt                #   FastAPI + Uvicorn dependencies
│   ├── data/
├── streamlit_app/                          # 🚀 NEW: Streamlit front-end
│   ├── app.py                              #   Web UI calling the FastAPI backend
│   ├── requirements.txt                    #   Streamlit + Requests dependencies
│   └── Dockerfile                          #   Streamlit container definition
├── Dockerfile                              # 🚀 NEW: FastAPI container definition
├── docker-compose.yaml                     # 🚀 NEW: Multi-service orchestration (FastAPI + Streamlit)
├── tasks.py
├── README.md
└── uv.lock
```

> Note: Any `.venv/` directory remains ignored and should not be committed.



## **Module Overview**

### 🧠 `src/api/` — FastAPI Inference Service

* Loads the trained model (`house_price_model.pkl`) and preprocessor.
* Exposes two routes:

  * **`/health`** — simple status check.
  * **`/predict`** — accepts JSON matching `HousePredictionRequest`, returns predicted price.
* Runs via **Uvicorn** in Docker on port `8000`.

### 🎨 `streamlit_app/` — Streamlit Frontend

* Provides an interactive dashboard for user input.
* Calls the FastAPI backend using the `API_URL` environment variable (e.g. `http://fastapi:8000`).
* Displays predicted price, confidence interval, and feature importance.
* Runs via **Streamlit** in Docker on port `8501`.



## **Docker & Compose Overview**

### 🧩 Dockerfiles

* **Root `Dockerfile`** → builds FastAPI backend.
* **`streamlit_app/Dockerfile`** → builds Streamlit frontend.

### ⚙️ `docker-compose.yaml`

Defines both containers and their networking:

```yaml
services:
  fastapi:
    build: .
    ports: ["8000:8000"]

  streamlit:
    build: ./streamlit_app
    ports: ["8501:8501"]
    environment:
      API_URL: http://fastapi:8000
    depends_on:
      - fastapi
```

Docker Compose automatically links the two containers, so the Streamlit UI can reach the FastAPI service via its hostname `fastapi`.



## **Build and Run the Application**

### 🏗️ Build both images

```bash
docker compose build
```

### 🚀 Run the full stack

```bash
docker compose up
# or detached:
docker compose up -d
```

### 🌐 Access the apps

| Service       | URL                                                      |
| - | -- |
| **FastAPI**   | [http://localhost:8000/docs](http://localhost:8000/docs) |
| **Streamlit** | [http://localhost:8501](http://localhost:8501)           |



## **Testing the FastAPI Endpoint**

### ✅ Health check

```bash
curl http://localhost:8000/health
```

### 🧠 Prediction request

```bash
curl -X POST "http://localhost:8000/predict" \
     -H "Content-Type: application/json" \
     -d '{"sqft":2000,"bedrooms":3,"bathrooms":2,"year_built":2010,"condition":"Good"}'
```

Expected response:

```json
{"predicted_price": 354820.45, "currency": "USD"}
```



## **Publishing to Docker Hub**

### 1️⃣ Log in

```bash
docker login
# username: ch3rrypi3
```

### 2️⃣ Push images

```bash
docker push ch3rrypi3/fastapi:dev
docker push ch3rrypi3/streamlit:dev
```

### 3️⃣ Verify

Check your repositories at
👉 [https://hub.docker.com/repositories/ch3rrypi3](https://hub.docker.com/repositories/ch3rrypi3)



## **Useful Docker Commands**

| Purpose                                 | Command                                   |
|  | -- |
| List running containers                 | `docker ps`                               |
| List all containers (including stopped) | `docker ps -a`                            |
| Stop containers                         | `docker compose down`                     |
| Remove all containers, images, networks | `docker system prune -a`                  |
| View image list                         | `docker images`                           |
| View logs (live)                        | `docker compose logs -f`                  |
| Build single image                      | `docker build -t ch3rrypi3/fastapi:dev .` |
| Push image to Docker Hub                | `docker push ch3rrypi3/fastapi:dev`       |



## ✅ Summary

With this stage, the project now delivers a **fully containerised, end-to-end ML application**:

* **FastAPI backend** for real-time inference.
* **Streamlit frontend** for an interactive UI.
* **Docker and Docker Compose** for seamless local orchestration.
* **Docker Hub** integration for image distribution and versioning.

The full MLOps lifecycle is now complete — from data ingestion and feature engineering to model training, deployment, and interactive visualisation. 🚀