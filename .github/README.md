# **GitHub Workflows & Secrets — Continuous Integration (CI) Configuration**

This folder contains the **continuous integration** configuration for the **MLOps House Price Prediction** project.
It includes automated workflows for **testing, data processing, model training, and container publishing** to **DockerHub** using **GitHub Actions**.

This guide also explains how to correctly set up your **DockerHub access token** and **GitHub repository secrets/variables**, which are required for the workflow to authenticate and push your final Docker image.

## **Folder Structure**

```
.github/
├── workflows/
│   └── ci.yml                     # CI pipeline definition
└── img/
    ├── dockerhub_username.png     # Example of DockerHub username under profile
    ├── dockerhub_token.png        # Token creation screen in DockerHub
    ├── github_secrets.png         # GitHub 'Secrets' tab view
    └── github_new_secret.png      # 'New repository secret' creation screen
```

## **Overview of CI Pipeline**

The **GitHub Actions workflow** (`ci.yml`) automatically runs when you push or merge changes. It performs the following steps:

1. 🧪 **Run unit tests** to verify the codebase integrity.
2. 🧹 **Preprocess data** and engineer features using `invoke`.
3. 🧠 **Train and log the model** with **MLflow** (running in a temporary Docker container).
4. 🏗️ **Build and publish** the resulting model image to **DockerHub**.

Each stage is represented as a job in the pipeline (`tests`, `data-processing`, `model-training`, `build-and-publish`).

To publish the image successfully, the workflow must be able to log in to DockerHub using two credentials:

* `DOCKERHUB_USERNAME` (stored as a **GitHub repository variable**)
* `DOCKERHUB_TOKEN` (stored as a **GitHub repository secret**)



## **1️⃣ Retrieve Your DockerHub Credentials**

Follow these steps to obtain your **DockerHub username** and **personal access token**.

### 🪪 Step 1 — Get Your Username

Log in to [DockerHub](https://hub.docker.com/).
Click the **top-right profile logo**. Your **username** appears immediately beneath your profile picture (as shown below).

<p align="center">
  <img src="img/dockerhub_username.png" alt="DockerHub username example" width="600"/>
</p>

For example, in this image, the username is **`ch3rrypi3`**.



### 🔐 Step 2 — Generate a Personal Access Token

1. Click your profile logo again.
2. Select **“Account settings.”**
3. In the sidebar, click **“Personal access tokens.”**
4. Click **“Generate new token.”**

<p align="center">
  <img src="img/dockerhub_token.png" alt="DockerHub token generation screen" width="700"/>
</p>

After generating it:

* ✅ **Copy** the token immediately — you won’t be able to view it again later.
* This token will be used as your **GitHub secret value** (`DOCKERHUB_TOKEN`).



## **2️⃣ Add DockerHub Credentials to Your GitHub Repository**

Next, add these credentials so GitHub Actions can authenticate and push images.

### ⚙️ Step 1 — Open Repository Settings

1. Navigate to your GitHub repository.
2. Click the **“Settings”** tab.
3. Under **Security**, expand **“Secrets and variables”** → click **“Actions.”**

<p align="center">
  <img src="img/github_secrets.png" alt="GitHub Secrets overview" width="700"/>
</p>



### 🔑 Step 2 — Add the DockerHub Token as a Secret

1. Under the **“Secrets”** tab, click **“New repository secret.”**
2. For **Name**, enter:

   ```
   DOCKERHUB_TOKEN
   ```
3. In the **Secret** field, paste your copied DockerHub token.
4. Click **“Add secret.”**

<p align="center">
  <img src="img/github_new_secret.png" alt="New GitHub secret creation" width="700"/>
</p>



### 🧩 Step 3 — Add the DockerHub Username as a Variable

1. In the same section, switch to the **“Variables”** tab.
2. Click **“New repository variable.”**
3. For **Name**, enter:

   ```
   DOCKERHUB_USERNAME
   ```
4. For **Value**, enter your DockerHub username (e.g., `ch3rrypi3`).
5. Click **“Add variable.”**



## **3️⃣ Running the Workflow**

Once your secrets and variables are configured, you can trigger the workflow:

### 🧪 Option A — Test on a non-main branch

From VS Code or your terminal:

```bash
git add .
git commit -m "Trigger CI pipeline test"
git push origin <branch-name>
```

This will execute the **tests**, **data-processing**, and **model-training** stages — but **skip the Docker publishing**, since it only runs on the main branch.



### 🚀 Option B — Publish to DockerHub via `main` branch

When you **merge** your feature branch into `main` (or push directly to `main`):

* The entire pipeline runs end-to-end.
* The final Docker image (`house-price-model`) is **built and published** to your **DockerHub repository** automatically.

You can then view it in your DockerHub account under:
👉 **Repositories → house-price-model**



## **✅ Summary**

This folder provides everything needed to **automate your MLOps CI/CD process** via GitHub Actions.

**Included:**

* `ci.yml` — complete multi-stage pipeline (test → process → train → publish)
* Image guides for **DockerHub token setup** and **GitHub secrets/variables**
* Step-by-step setup instructions for secure authentication

Once configured, every push or merge will trigger your workflow automatically — ensuring reproducible, **continuous integration** of your **House Price Prediction** model. 🚀


