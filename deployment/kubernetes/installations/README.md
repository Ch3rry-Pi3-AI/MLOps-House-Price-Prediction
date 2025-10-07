# ☸️ **KinD & kubectl — Local Kubernetes Setup on Windows**

This guide explains how to install and configure **KinD (Kubernetes-in-Docker)** and **kubectl** on **Windows**, allowing you to create and manage a fully functional local **Kubernetes cluster** for development and testing.



## 🧠 **Overview**

| Tool        | Description                                                                                                           |
| -- |  |
| **KinD**    | *(Kubernetes in Docker)* — Creates lightweight Kubernetes clusters inside Docker containers.                          |
| **kubectl** | The official Kubernetes command-line client used to control clusters (create pods, apply manifests, view logs, etc.). |

Both are independent but complementary:

> 🧩 **KinD** creates the cluster → **kubectl** connects and manages it.



## 🐳 **1. Prerequisites**

Before installing, ensure your system meets the following:

| Requirement                | Description                                | Command / Link                                                             |
| -- |  | -- |
| **Docker Desktop**         | Required backend for KinD node containers. | [Download Docker Desktop](https://www.docker.com/products/docker-desktop/) |
| **PowerShell (Admin)**     | Used for running commands.                 | `Start-Process powershell -Verb runAs`                                     |
| **Windows 10/11 (64-bit)** | Required for modern KinD versions.         | —                                                                          |



## ⚡ **2. Install kubectl (Kubernetes CLI)**

`kubectl` is the official CLI for managing Kubernetes clusters.

### 🔹 Step 1 — Download the Binary

Run the following in **PowerShell**:

```powershell
curl.exe -LO "https://dl.k8s.io/release/v1.34.0/bin/windows/amd64/kubectl.exe"
```

This downloads version 1.34.0 of `kubectl.exe` for Windows.

### 🔹 Step 2 — Move kubectl to a Folder on PATH

```powershell
Move-Item .\kubectl.exe "C:\Program Files\kubectl.exe"
```

Then verify installation:

```powershell
kubectl version
```

✅ **Example output:**

```
Client Version: v1.34.0
Kustomize Version: v5.7.1
Unable to connect to the server: dial tcp [::1]:8080: connectex: No connection could be made because the target machine actively refused it.
```

🟡 **Explanation:**
This message simply means there is **no Kubernetes cluster** yet — `kubectl` is installed and working, but has nothing to connect to. Once KinD creates a cluster, this will succeed.

📘 **Official documentation:**
👉 [Install and Set Up kubectl on Windows](https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/)



### 🧩 **Check kubectl Help Menu**

Run:

```powershell
kubectl
```

✅ **Example output (truncated):**

```
kubectl controls the Kubernetes cluster manager.

Basic Commands (Beginner):
  create          Create a resource from a file or from stdin
  get             Display one or many resources
  delete          Delete resources by file names, stdin, or label selector

Cluster Management Commands:
  cluster-info    Display cluster information
  top             Display resource (CPU/memory) usage
  drain           Drain node in preparation for maintenance

Advanced Commands:
  apply           Apply a configuration to a resource by file name or stdin
  kustomize       Build a kustomization target from a directory or URL
```



## 🚀 **3. Install KinD (Kubernetes in Docker)**

KinD runs a full Kubernetes cluster inside Docker — ideal for local testing, CI/CD pipelines, and MLOps development.

### 🔹 Option 1 — Install with Chocolatey

If you use **Chocolatey**:

```powershell
choco install kind
```

### 🔹 Option 2 — Manual Installation

```powershell
curl.exe -Lo kind-windows-amd64.exe https://kind.sigs.k8s.io/dl/v0.30.0/kind-windows-amd64
Move-Item .\kind-windows-amd64.exe "C:\Program Files\kind.exe"
```

Then verify:

```powershell
kind version
```

✅ **Example output:**

```
(MLOps-House-Price-Prediction) PS C:\Users\HP\OneDrive\Documents\Projects\MLOps\MLOps-House-Price-Prediction> kind version
kind v0.30.0 go1.24.6 windows/amd64
```



### 🧭 **Check KinD Help Menu**

Run:

```powershell
kind
```

✅ **Example output (truncated):**

```
kind creates and manages local Kubernetes clusters using Docker container 'nodes'

Available Commands:
  build       Build one of [node-image]
  create      Creates one of [cluster]
  delete      Deletes one of [cluster]
  get         Gets one of [clusters, nodes, kubeconfig]
  load        Loads images into nodes
  version     Prints the kind CLI version
```



## 🏗️ **4. Create a KinD Cluster**

Now that both tools are installed, create your local test cluster:

```powershell
kind create cluster --name test
```

✅ **Example output:**

```
Creating cluster "test" ...
 • Ensuring node image (kindest/node:v1.34.0) 🖼  ...
 ✓ Ensuring node image (kindest/node:v1.34.0) 🖼
 • Preparing nodes 📦   ...
 ✓ Preparing nodes 📦 
 • Writing configuration 📜  ...
 ✓ Writing configuration 📜
 • Starting control-plane 🕹️  ...
 ✓ Starting control-plane 🕹️
 • Installing CNI 🔌  ...
 ✓ Installing CNI 🔌
 • Installing StorageClass 💾  ...
 ✓ Installing StorageClass 💾
Set kubectl context to "kind-test"
You can now use your cluster with:

kubectl cluster-info --context kind-test

Have a nice day! 👋
```

KinD automatically updates your kubeconfig file at:

```
%USERPROFILE%\.kube\config
```

This file allows `kubectl` to connect to the new cluster.



## 🔍 **5. Verify Cluster Connectivity**

Once your cluster is running, confirm everything is working.

### 🔹 Step 1 — Check Cluster Info

```powershell
kubectl cluster-info
```

✅ **Example output:**

```
Kubernetes control plane is running at https://127.0.0.1:56652
CoreDNS is running at https://127.0.0.1:56652/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```

*(If you see this, your cluster is healthy.)*

### 🔹 Step 2 — Check Nodes

```powershell
kubectl get nodes
```

✅ **Example output:**

```
NAME                 STATUS   ROLES           AGE   VERSION
test-control-plane   Ready    control-plane   50s   v1.34.0
```



## 🧰 **6. Useful Commands**

| Command                                | Description                          |
| -- |  |
| `kubectl version --output=yaml`        | Show detailed client/server versions |
| `kubectl config get-contexts`          | List available cluster contexts      |
| `kubectl config use-context kind-test` | Switch to the KinD cluster context   |
| `kind get clusters`                    | List all KinD clusters               |
| `docker ps`                            | View running KinD node containers    |



## 🧹 **7. Delete the Cluster**

When you are finished, delete the test cluster:

```powershell
kind delete cluster --name test
```

✅ **Example output:**

```
Deleting cluster "test" ...
Deleted nodes: ["test-control-plane"]
```

All Docker containers and resources associated with the cluster are now removed.



## ✅ **Summary**

| Component          | Role                                            |
|  | -- |
| **kubectl**        | CLI for managing Kubernetes clusters.           |
| **KinD**           | Creates local Kubernetes clusters using Docker. |
| **Docker Desktop** | Container engine required by KinD.              |

You now have a **fully functional local Kubernetes environment** ready for:

* Deploying your MLOps applications (e.g., FastAPI + Streamlit).
* Testing configuration manifests and deployment strategies.
* Experimenting safely without incurring any cloud costs.
