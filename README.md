# **Kubernetes — Scalable Production Inference (Deployment Stage)**

This branch adds a **scalable, production-style inference stack** using **Kubernetes**.
You’ll spin up a **three-node KinD cluster**, deploy the **FastAPI model service** and **Streamlit UI** as Kubernetes **Deployments + Services**, and expose them via **NodePorts** for local access.

* We install **KinD** and **kubectl** (see `deployment/kubernetes/installations/`).
* We launch the cluster from the **KinD config** (three nodes).
* We generate **manifests** declaratively from imperative commands.
* We **apply** the manifests to create the in-cluster services.
* We access the **Streamlit** and **FastAPI** endpoints locally.



## **Project Structure**

```
mlops-house-price-prediction/
├── deployment/
│   └── kubernetes/
│       ├── kind/
│       │   └── kind-three-node-cluster.yaml     # KinD 3-node cluster config (1 control-plane + 2 workers)
│       ├── installations/                       # KinD & kubectl install guides (Windows)
│       ├── kubectl/                             # kubectl cheat-sheet for this project
│       ├── model-deploy.yaml                    # FastAPI model Deployment
│       ├── model-svc.yaml                       # FastAPI Service (NodePort 30100)
│       ├── streamlit-deploy.yaml                # Streamlit UI Deployment
│       └── streamlit-svc.yaml                   # Streamlit Service (NodePort 30000)
├── src/                                         
├── streamlit_app/                               
├── Dockerfile                                   
├── docker-compose.yaml                          
└── README.md
```



## **Overview & Commands**

### 1) Install tools (KinD & kubectl)

See **installation steps** in:

* `deployment/kubernetes/installations/`

  * **KinD** quick start
  * **kubectl** on Windows (with official link)

### 2) Launch the 3-node cluster (KinD)

From the **repo root**:

```powershell
kind create cluster --config deployment/kubernetes/kind/kind-three-node-cluster.yaml
kubectl get nodes
```

You should see `kind-control-plane`, `kind-worker`, and `kind-worker2` in **Ready** state.

### 3) Build manifests (declarative from imperative)

From `deployment/kubernetes/` (adjust image tags as needed):

```powershell
# FastAPI Model
kubectl create deployment model `
  --image=ch3rrypi3/house-price-model:latest `
  --port=8000 --replicas=2 `
  --dry-run=client -o yaml > model-deploy.yaml

kubectl create service nodeport model `
  --tcp=8000 --node-port=30100 `
  --dry-run=client -o yaml > model-svc.yaml

# Streamlit UI (ensure app points to http://model:8000 inside cluster)
kubectl create deployment streamlit `
  --image=ch3rrypi3/streamlit:v1 `
  --port=8501 --replicas=2 `
  --dry-run=client -o yaml > streamlit-deploy.yaml

kubectl create service nodeport streamlit `
  --tcp=8501 --node-port=30000 `
  --dry-run=client -o yaml > streamlit-svc.yaml
```

> Tip: Inside the Streamlit app, set
> `DEFAULT_API_URL = os.getenv("API_URL", "http://model:8000")`
> so it talks to the in-cluster **model** service.

### 4) Apply the manifests

From the **repo root** (or from `deployment/kubernetes/` with relative paths):

```powershell
kubectl apply -f deployment/kubernetes/model-deploy.yaml `
              -f deployment/kubernetes/model-svc.yaml `
              -f deployment/kubernetes/streamlit-deploy.yaml `
              -f deployment/kubernetes/streamlit-svc.yaml

kubectl get pods -w
kubectl get svc
```

### 5) Access the UIs (NodePort)

* **Streamlit UI:** [http://localhost:30000](http://localhost:30000)
* **FastAPI model API:** [http://localhost:30100](http://localhost:30100)



## **Delete the cluster (cleanup)**

```powershell
kind delete cluster --name kind
```

This removes the control plane, workers, and related resources created by KinD.



### **Summary**

* ✅ Installed **KinD** and **kubectl** (see `installations/`).
* 🚀 Launched a **3-node** KinD cluster from `kind-three-node-cluster.yaml`.
* 🧱 Generated Deployment/Service **manifests** (model + streamlit).
* 📦 Applied manifests to create **scalable** deployments.
* 🌐 Accessed services via **NodePorts** at **30000** (Streamlit) and **30100** (FastAPI).
* 🧹 Cleaned up with `kind delete cluster --name kind`.

This stage delivers a **reproducible, scalable inference environment** ready for further automation and observability.