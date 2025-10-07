# ☸️ **Kubernetes Cluster Setup (KinD - Three Node Cluster)**

This guide explains how to **create**, **configure**, and **deploy** your local Kubernetes cluster for the **MLOps House Price Prediction** project using **KinD (Kubernetes-in-Docker)**.



## 📂 **Folder Structure**

```
MLOps-House-Price-Prediction/
├── deployment/
│   └── kubernetes/
│       ├── kind/
│       │   └── kind-three-node-cluster.yaml     # KinD cluster configuration file
│       ├── installations/                       # Folder for installation guides or setup scripts
│       ├── kubectl/                             # Folder for kubectl command references or helpers
│       ├── model-deploy.yaml                    # FastAPI model deployment
│       ├── model-svc.yaml                       # FastAPI service
│       ├── streamlit-deploy.yaml                # Streamlit UI deployment
│       └── streamlit-svc.yaml                   # Streamlit service
```



## 🚀 **1. Create the Cluster**

From the **project root** (using Powershell for Windows), run:

```powershell
kind create cluster --config deployment/kubernetes/kind/kind-three-node-cluster.yaml
```

✅ This will:

* Create a **3-node cluster** (1 control plane + 2 workers).
* Set your kubectl context automatically to `kind-kind`.
* Install core components (CNI, storage class, etc.).

Check it’s running:

```powershell
kubectl get nodes
```

Example output:

```
NAME                 STATUS   ROLES           AGE   VERSION
kind-control-plane   Ready    control-plane   1m    v1.34.0
kind-worker          Ready    <none>          1m    v1.34.0
kind-worker2         Ready    <none>          1m    v1.34.0
```



## 📦 **2. Deploy All Services**

After the cluster launches, apply all manifests in order:

```powershell
kubectl apply -f deployment/kubernetes/model-deploy.yaml `
              -f deployment/kubernetes/model-svc.yaml `
              -f deployment/kubernetes/streamlit-deploy.yaml `
              -f deployment/kubernetes/streamlit-svc.yaml
```

Watch as pods start:

```powershell
kubectl get pods -w
```

✅ Expected:

```
model-xxxxxx        1/1   Running
streamlit-xxxxxx    1/1   Running
```



## 🌐 **3. Access the Applications**

Check service ports:

```powershell
kubectl get svc
```

Typical output:

```
NAME         TYPE       CLUSTER-IP      EXTERNAL-IP   PORT(S)          AGE
model        NodePort   10.96.221.94    <none>        8000:30100/TCP   1m
streamlit    NodePort   10.96.182.193   <none>        8501:30000/TCP   1m
```

* 🧠 **FastAPI model service:** [http://localhost:30100](http://localhost:30100)
* 💻 **Streamlit UI:** [http://localhost:30000](http://localhost:30000)



## 🧹 **4. Delete the Cluster**

When you’re finished, cleanly remove the KinD cluster:

```powershell
kind delete cluster --name kind
```

✅ Expected:

```
Deleting cluster "kind" ...
Deleted nodes: ["kind-control-plane", "kind-worker", "kind-worker2"]
```



## ✅ **Summary**

| Step                | Command                                                                                | Description                |
| - | -- | -- |
| 🧱 Create cluster   | `kind create cluster --config deployment/kubernetes/kind/kind-three-node-cluster.yaml` | Builds 3-node KinD cluster |
| 📦 Deploy manifests | `kubectl apply -f …`                                                                   | Deploys model + Streamlit  |
| 🔍 Check pods       | `kubectl get pods -w`                                                                  | Monitors status            |
| 🧹 Delete cluster   | `kind delete cluster --name kind`                                                      | Removes all KinD resources |