# ☸️ **KinD Cluster Configuration**

This folder contains the **KinD (Kubernetes-in-Docker)** configuration used to launch a **three-node Kubernetes cluster** — one control plane and two worker nodes — for local testing and development. For Windows, user PowerShell.



## 🚀 **Create the Cluster**

From the **project root**, run:

```powershell
kind create cluster --config deployment/kubernetes/kind/kind-three-node-cluster.yaml
```

✅ This will:

* Initialise a **3-node cluster** inside Docker containers.
* Automatically set the `kubectl` context to `kind-kind`.

Verify setup:

```powershell
kubectl get nodes
```



## 🧹 **Delete the Cluster**

When finished, remove the cluster cleanly:

```powershell
kind delete cluster --name kind
```

✅ Expected:

```
Deleting cluster "kind" ...
Deleted nodes: ["kind-control-plane", "kind-worker", "kind-worker2"]
```



**Note:**
This configuration is used by other deployment manifests in
`deployment/kubernetes/` to deploy the FastAPI model and Streamlit UI services.