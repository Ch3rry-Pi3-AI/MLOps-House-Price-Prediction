# ☸️ kubectl — Commands & Workflows (Local KinD Cluster)

This folder documents **kubectl** commands used to manage the local Kubernetes environment for the **MLOps House Price Prediction** project. It includes:

* Quick verification commands
* Imperative workflows (create/scale/expose)
* Declarative workflows (create YAML via `--dry-run`, then `apply`)
* Image updates and rollout management
* Typical outputs so you know what “good” looks like

> ✳️ Prerequisite: A KinD cluster is already running and your context is set to `kind-kind`. See the `kind/` README for cluster lifecycle.



## 1) Verify the cluster

```powershell
kubectl cluster-info
```

**Example output**

```
Kubernetes control plane is running at https://127.0.0.1:59749
CoreDNS is running at https://127.0.0.1:59749/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```

```powershell
kubectl get nodes
```

**Example**

```
NAME                 STATUS   ROLES           AGE   VERSION
kind-control-plane   Ready    control-plane   71s   v1.34.0
kind-worker          Ready    <none>          57s   v1.34.0
kind-worker2         Ready    <none>          58s   v1.34.0
```

```powershell
kubectl get pods -A
```

**Example (system pods)**

```
NAMESPACE            NAME                                         READY   STATUS    RESTARTS   AGE
kube-system          coredns-66bc5c9577-6p4xn                     1/1     Running   0          3m23s
kube-system          etcd-kind-control-plane                      1/1     Running   0          3m29s
...
local-path-storage   local-path-provisioner-7b8c8ddbd6-67fnf      1/1     Running   0          3m23s
```



## 2) Imperative: deploy Streamlit, scale, delete a pod, expose via NodePort

### Create Streamlit Deployment

```powershell
kubectl create deployment streamlit --image=ch3rrypi3/streamlit:dev
```

```powershell
kubectl get all
```

**Example (initially creating)**

```
NAME                             READY   STATUS              RESTARTS   AGE
pod/streamlit-54f7c677db-6lb49   0/1     ContainerCreating   0          31s
...
deployment.apps/streamlit        0/1     1            0      31s
```

**Once ready**

```powershell
kubectl get deploy
```

```
NAME        READY   UP-TO-DATE   AVAILABLE   AGE
streamlit   1/1     1            1           3m10s
```

### Inspect Deployment

```powershell
kubectl describe deploy streamlit
```

**Example (abridged)**

```
Name:                   streamlit
Labels:                 app=streamlit
Replicas:               1 desired | 1 available
Containers:
  streamlit:
    Image:  ch3rrypi3/streamlit:dev
Conditions:
  Available  True    MinimumReplicasAvailable
  Progressing True   NewReplicaSetAvailable
```

### Scale up to 3

```powershell
kubectl scale deploy streamlit --replicas=3
kubectl get all
```

**Example**

```
deployment.apps/streamlit   3/3   3   3   10m
replicaset.apps/streamlit-54f7c677db   3   3   3   10m
```

### Delete one pod (ReplicaSet will recreate it)

```powershell
kubectl delete pod <one-streamlit-pod-name>
kubectl get pods
```

**Example**

```
pod "streamlit-...-6lb49" deleted
NAME                         READY   STATUS    RESTARTS   AGE
streamlit-...-7l4kv          1/1     Running   0          2m29s
streamlit-...-lxsw8          1/1     Running   0          5s    ← new
streamlit-...-rwwm7          1/1     Running   0          2m29s
```

### Expose Streamlit via NodePort (port 8501 → 30000)

```powershell
kubectl scale deploy streamlit --replicas=2
kubectl create service nodeport streamlit --tcp=8501 --node-port=30000
kubectl get svc streamlit
```

**Example**

```
NAME         TYPE      CLUSTER-IP       EXTERNAL-IP   PORT(S)          AGE
streamlit    NodePort  10.96.182.193    <none>        8501:30000/TCP   15s
```

Open: **[http://localhost:30000/](http://localhost:30000/)**

> 📝 **Tip:** Default NodePort range is **30000–32767**. If you use `--node-port=3000`, Kubernetes will reject it.



## 3) Imperative: deploy the Model API + Service

```powershell
kubectl create deployment model --image=ch3rrypi3/house-price-model:latest --port=8000 --replicas=2
kubectl create service nodeport model --tcp=8000 --node-port=30100
kubectl get svc model
```

**Example**

```
NAME    TYPE      CLUSTER-IP     EXTERNAL-IP   PORT(S)          AGE
model   NodePort  10.96.221.94   <none>        8000:30100/TCP   1m
```

Open: **[http://localhost:30100/](http://localhost:30100/)**



## 4) Point Streamlit to the in-cluster Model Service & update image

In your `streamlit_app/app.py`, update:

```python
# -
# Constants & Helpers
# -
DEFAULT_API_URL = os.getenv("API_URL", "http://model:8000")  # ← in-cluster DNS
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_MODEL   = os.getenv("APP_MODEL", "XGBoost")
```

Rebuild and push the image:

```powershell
docker image build -t ch3rrypi3/streamlit:v1 .
docker push ch3rrypi3/streamlit:v1
```

Update the running Deployment to use `v1`:

```powershell
kubectl set image deploy streamlit streamlit=ch3rrypi3/streamlit:v1
kubectl rollout status deploy/streamlit
```



## 5) Declarative: generate manifests with `--dry-run`, then `apply`

Create YAMLs (note corrected names & ports):

```bash
# Model Service (NodePort 30100)
kubectl create service nodeport model \
  --tcp=8000 --node-port=30100 \
  --dry-run=client -o yaml > model-svc.yaml

# Model Deployment
kubectl create deployment model \
  --image=ch3rrypi3/house-price-model:latest --port=8000 --replicas=2 \
  --dry-run=client -o yaml > model-deploy.yaml

# Streamlit Service (NodePort 30000)
kubectl create service nodeport streamlit \
  --tcp=8501 --node-port=30000 \
  --dry-run=client -o yaml > streamlit-svc.yaml

# Streamlit Deployment (ensure correct image name)
kubectl create deployment streamlit \
  --image=ch3rrypi3/streamlit:v1 --port=8501 --replicas=2 \
  --dry-run=client -o yaml > streamlit-deploy.yaml
```

> ⚠️ **Gotchas to avoid**
>
> * Use **`:`** for tags (`:latest`), not `/latest`.
> * Ensure the repo is **`ch3rrypi3/streamlit`** (not `steamlit`) and the file name **`streamlit-deploy.yaml`** (not `steamlit-deploy.yaml`).
> * Keep NodePorts within **30000–32767**.

Apply all at once:

```powershell
kubectl apply -f model-deploy.yaml `
              -f model-svc.yaml `
              -f streamlit-deploy.yaml `
              -f streamlit-svc.yaml
```

**Example output**

```
deployment.apps/model unchanged
service/model unchanged
deployment.apps/streamlit configured
Warning: resource services/streamlit is missing the kubectl.kubernetes.io/last-applied-configuration annotation...
service/streamlit configured
```

> ℹ️ The warning appears when a resource was created imperatively (e.g., `kubectl create ...`) and is later “adopted” by `apply`. Kubernetes patches the missing annotation; subsequent `apply` runs will be clean.



## 6) Everyday useful kubectl commands

| Goal                        | Command                                                               |
|  |  |
| Watch pods in real time     | `kubectl get pods -w`                                                 |
| Describe a pod/deployment   | `kubectl describe pod <name>` / `kubectl describe deploy <name>`      |
| Check services & ports      | `kubectl get svc`                                                     |
| Update image                | `kubectl set image deploy streamlit streamlit=ch3rrypi3/streamlit:v1` |
| Restart a deployment        | `kubectl rollout restart deploy streamlit`                            |
| Rollout status              | `kubectl rollout status deploy/streamlit`                             |
| View logs                   | `kubectl logs <pod-name>`                                             |
| Delete one bad pod          | `kubectl delete pod <pod-name>` (ReplicaSet recreates it)             |
| Scale replicas              | `kubectl scale deploy streamlit --replicas=2`                         |
| Apply a folder of YAMLs     | `kubectl apply -f deployment/kubernetes/`                             |
| Delete resources from YAMLs | `kubectl delete -f deployment/kubernetes/`                            |
| Current context             | `kubectl config current-context`                                      |



## 7) Troubleshooting quick hits

* **`ImagePullBackOff`**
  Check image name & tag, push to Docker Hub, or `kind load docker-image <image>:<tag> --name kind`.
* **NodePort not created**
  Ensure `--node-port` is in **30000–32767**.
* **`kubectl apply` warning about last-applied**
  Harmless on first `apply` after an imperative `create`; it will be patched.
