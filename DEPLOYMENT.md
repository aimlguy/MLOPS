# 🚀 Cloud Run Deployment - Quick Start Guide

## Overview
Deploy the No-Show Prediction API to Google Cloud Run with automatic CI/CD and dynamic model loading from MLflow.

---

## 📋 Quick Setup Checklist

### 1️⃣ GCP Setup (5 minutes)
```bash
# Set your project ID
export PROJECT_ID="your-project-id"
export REGION="us-central1"

# Enable APIs
gcloud services enable run.googleapis.com artifactregistry.googleapis.com

# Create Artifact Registry
gcloud artifacts repositories create mlops-models \
  --repository-format=docker \
  --location=$REGION

# Create service account
gcloud iam service-accounts create mlops-deployer \
  --display-name="MLOps Deployer"

# Grant permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:mlops-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:mlops-deployer@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

# Generate key
gcloud iam service-accounts keys create gcp-key.json \
  --iam-account=mlops-deployer@$PROJECT_ID.iam.gserviceaccount.com
```

### 2️⃣ GitHub Secrets (2 minutes)
Go to: **Settings → Secrets and variables → Actions → New repository secret**

Add these secrets:
- `GCP_PROJECT_ID`: Your GCP project ID
- `GCP_SA_KEY`: Contents of `gcp-key.json` file
- `GCP_SERVICE_ACCOUNT_EMAIL`: `mlops-deployer@your-project-id.iam.gserviceaccount.com`

### 3️⃣ Deploy (automatic on push)
```bash
git add .
git commit -m "Deploy to Cloud Run"
git push origin main
```

---

## 🎯 Key Features

### ✅ Dynamic Model Loading
The API automatically serves the latest **Production** model from MLflow:
- No code changes needed when promoting models
- Zero-downtime model updates
- Automatic fallback to latest model if no Production model exists

### ✅ Three GitHub Actions Workflows

#### 1. **CI Pipeline** (`.github/workflows/ci.yml`)
Runs on every push/PR:
- Code linting (Black, Flake8)
- Type checking (mypy)
- Unit tests
- Docker build validation

#### 2. **CD Pipeline** (`.github/workflows/deploy-gcp.yml`)
Deploys on push to `main`:
- Builds Docker image
- Pushes to Artifact Registry
- Deploys to Cloud Run
- Runs health checks

#### 3. **Model Promotion** (`.github/workflows/model-promotion.yml`)
Triggers after promoting model:
- Reloads model in running service
- No redeployment needed
- Verifies new model is loaded

---

## 🔄 Model Promotion Workflow

### Step 1: Train and Promote Model
```python
# In your training script
from src.train import train_and_promote_if_better

# This automatically promotes if AUC is better than Production
promoted_version = train_and_promote_if_better("data/raw/noshow.csv")

if promoted_version:
    print(f"✅ Model v{promoted_version} promoted!")
```

### Step 2: Trigger Redeployment
**Option A: Automatic (using script)**
```bash
python scripts/trigger_model_deployment.py \
  --model-version v3 \
  --repo-owner your-username \
  --repo-name MLops
```

**Option B: Manual (GitHub UI)**
1. Go to **Actions** tab
2. Select **Model Promotion Auto-Deploy**
3. Click **Run workflow**
4. Enter model version

**Option C: Direct API call**
```bash
SERVICE_URL=$(gcloud run services describe noshow-prediction-api \
  --region us-central1 --format 'value(status.url)')

curl -X POST "$SERVICE_URL/reload-model"
```

---

## 🧪 Testing

### Test Local Build
```powershell
# Windows
.\scripts\test-local-deployment.ps1

# Linux/Mac
bash scripts/test-local-deployment.sh
```

### Test Production Endpoint
```bash
# Get service URL
SERVICE_URL=$(gcloud run services describe noshow-prediction-api \
  --region us-central1 --format 'value(status.url)')

# Health check
curl $SERVICE_URL/health

# Prediction
curl -X POST "$SERVICE_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 12345,
    "gender": "F",
    "age": 45,
    "scheduled_day": "2025-12-27T10:00:00",
    "appointment_day": "2026-01-05T14:00:00",
    "neighbourhood": "Downtown",
    "scholarship": false,
    "hypertension": true,
    "diabetes": false,
    "alcoholism": false,
    "handicap": 0,
    "sms_received": true
  }'
```

---

## 📊 Monitoring

### View Logs
```bash
gcloud run services logs read noshow-prediction-api \
  --region us-central1 \
  --limit 50
```

### Check Metrics (Console)
```
https://console.cloud.google.com/run/detail/us-central1/noshow-prediction-api
```

### Monitor Model Info
```bash
curl $SERVICE_URL/health | jq .model_info
```

---

## 🔧 Configuration

### Environment Variables (in Cloud Run)
- `MODEL_NAME`: MLflow model name (default: `noshow-prediction-model`)
- `MLFLOW_TRACKING_URI`: MLflow tracking URI (default: `file:///app/mlruns`)
- `PORT`: Service port (Cloud Run sets to 8080)

### Modify in `.github/workflows/deploy-gcp.yml`:
```yaml
--set-env-vars "MODEL_NAME=your-model-name,MLFLOW_TRACKING_URI=your-uri"
```

---

## 🚨 Troubleshooting

### Issue: Model not loading
**Check MLflow registry:**
```python
import mlflow
mlflow.set_tracking_uri("file:///path/to/mlruns")
client = mlflow.MlflowClient()
versions = client.get_latest_versions("noshow-prediction-model", stages=["Production"])
print(versions)
```

### Issue: Deployment fails
**Check logs:**
```bash
gcloud run services logs read noshow-prediction-api --region us-central1
```

### Issue: GitHub Actions fails
**Check secrets are set correctly:**
- Go to Settings → Secrets and variables → Actions
- Verify all three secrets exist
- Re-create `GCP_SA_KEY` if authentication fails

---

## 📚 File Structure

```
MLops/
├── .github/workflows/
│   ├── ci.yml                    # CI pipeline
│   ├── deploy-gcp.yml            # CD deployment
│   └── model-promotion.yml       # Model reload workflow
├── docker/
│   └── Dockerfile                # Production container
├── src/
│   ├── predict.py                # FastAPI app with dynamic loading
│   ├── train.py                  # Training with auto-promotion
│   ├── model_registry.py         # MLflow registry helpers
│   └── feature_engineering.py    # Feature pipeline
├── scripts/
│   ├── trigger_model_deployment.py    # GitHub Actions trigger
│   ├── test-local-deployment.ps1      # Windows test script
│   └── test-local-deployment.sh       # Linux/Mac test script
├── docs/
│   └── GCP_DEPLOYMENT_GUIDE.md   # Detailed documentation
├── requirements.txt               # Python dependencies
└── .dockerignore                  # Docker build optimization
```

---

## 🎓 Academic Value

This deployment demonstrates:

1. **Containerization**: Multi-stage Docker builds
2. **CI/CD**: Automated testing and deployment
3. **Model Registry**: MLflow for model versioning
4. **Dynamic Loading**: Zero-downtime model updates
5. **Cloud Deployment**: Serverless with Cloud Run
6. **Monitoring**: Health checks and logging
7. **Security**: Service accounts and least privilege

---

## 💰 Cost Estimates

- **Free Tier**: 2M requests/month free
- **Typical Cost**: $0.05 - $0.20 per 1K requests
- **Scales to Zero**: No cost when idle

---

## ✅ Verification Steps

After deployment:
- [ ] GitHub Actions CI passes
- [ ] GitHub Actions CD deploys successfully
- [ ] Cloud Run service is accessible via HTTPS
- [ ] `/health` endpoint returns 200
- [ ] `/predict` endpoint accepts requests
- [ ] Model info shows correct version
- [ ] Logs show model loaded successfully
- [ ] Model reload endpoint works

---

## 🎉 Next Steps

1. ✅ Deploy to Cloud Run (completed with this guide)
2. 🔄 Train baseline, improved, and best models
3. 📊 Set up Great Expectations for data validation
4. 🌊 Create Airflow DAG for scheduled retraining
5. 📈 Add monitoring and alerting
6. 🧪 Implement A/B testing between models

---

**For detailed setup instructions, see [docs/GCP_DEPLOYMENT_GUIDE.md](docs/GCP_DEPLOYMENT_GUIDE.md)**
