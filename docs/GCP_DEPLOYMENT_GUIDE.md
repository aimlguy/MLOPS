# 🚀 Google Cloud Platform Deployment Guide

## Overview
This guide walks you through deploying the No-Show Prediction MLOps pipeline to Google Cloud Run with automatic CI/CD using GitHub Actions.

---

## 📋 Prerequisites

1. **Google Cloud Project**
   - Active GCP project with billing enabled
   - Project ID (e.g., `my-mlops-project-12345`)

2. **Local Tools**
   - Google Cloud SDK (`gcloud`) installed
   - Docker installed
   - Git configured

3. **GitHub Repository**
   - Repository pushed to GitHub
   - Admin access to configure secrets

---

## 🔧 GCP Setup (One-Time Configuration)

### Step 1: Set Project Variables
```bash
export PROJECT_ID="your-gcp-project-id"
export REGION="us-central1"
export SERVICE_ACCOUNT_NAME="mlops-deployer"
export ARTIFACT_REPO="mlops-models"
```

### Step 2: Enable Required APIs
```bash
gcloud config set project $PROJECT_ID

gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  cloudbuild.googleapis.com \
  iam.googleapis.com
```

### Step 3: Create Artifact Registry Repository
```bash
gcloud artifacts repositories create $ARTIFACT_REPO \
  --repository-format=docker \
  --location=$REGION \
  --description="MLOps Docker images"
```

### Step 4: Create Service Account for GitHub Actions
```bash
gcloud iam service-accounts create $SERVICE_ACCOUNT_NAME \
  --display-name="MLOps GitHub Actions Deployer"

# Grant necessary permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"

gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"
```

### Step 5: Generate Service Account Key
```bash
gcloud iam service-accounts keys create gcp-key.json \
  --iam-account=$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com

# ⚠️ IMPORTANT: Keep this file secure - it contains credentials
```

### Step 6: Create Runtime Service Account (for Cloud Run)
```bash
gcloud iam service-accounts create noshow-api-runtime \
  --display-name="No-Show API Runtime"

export RUNTIME_SA_EMAIL="noshow-api-runtime@$PROJECT_ID.iam.gserviceaccount.com"
```

---

## 🔐 GitHub Secrets Configuration

Navigate to: **GitHub Repository → Settings → Secrets and variables → Actions**

Add the following secrets:

| Secret Name | Value | How to Get |
|-------------|-------|------------|
| `GCP_PROJECT_ID` | Your GCP project ID | `echo $PROJECT_ID` |
| `GCP_SA_KEY` | Contents of `gcp-key.json` | `cat gcp-key.json` |
| `GCP_SERVICE_ACCOUNT_EMAIL` | Runtime service account email | `echo $RUNTIME_SA_EMAIL` |

---

## 🏗️ Local Testing (Optional)

### Build Docker Image Locally
```bash
docker build -f docker/Dockerfile -t noshow-predictor:local .
```

### Run Locally
```bash
docker run -p 8080:8080 \
  -e MODEL_NAME=noshow-prediction-model \
  -e MLFLOW_TRACKING_URI=file:///app/mlruns \
  noshow-predictor:local
```

### Test Endpoints
```bash
# Health check
curl http://localhost:8080/health

# Prediction (example)
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 12345,
    "gender": "F",
    "age": 45,
    "scheduled_day": "2025-01-01T10:00:00",
    "appointment_day": "2025-01-15T14:00:00",
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

## 🚀 Deployment Workflow

### Automatic Deployment
Push changes to `main` branch triggers automatic deployment:
```bash
git add .
git commit -m "Deploy to Cloud Run"
git push origin main
```

### Manual Deployment
Trigger via GitHub Actions UI:
1. Go to **Actions** tab
2. Select **Deploy to Cloud Run**
3. Click **Run workflow**

---

## 🔄 Model Promotion Workflow

### When a New Model is Promoted to Production:

**Option 1: Manual Trigger**
1. Go to **Actions** → **Model Promotion Auto-Deploy**
2. Click **Run workflow**
3. Enter model version (e.g., `v3`)

**Option 2: Automatic (using script)**
```bash
# After promoting model in MLflow
gh workflow run model-promotion.yml \
  -f model_version="v3"
```

**Option 3: Direct API Call**
```bash
# Get Cloud Run service URL
SERVICE_URL=$(gcloud run services describe noshow-prediction-api \
  --region us-central1 \
  --format 'value(status.url)')

# Trigger model reload
curl -X POST "$SERVICE_URL/reload-model"
```

---

## 📊 Monitoring & Verification

### Get Service URL
```bash
gcloud run services describe noshow-prediction-api \
  --region us-central1 \
  --format 'value(status.url)'
```

### Check Service Health
```bash
SERVICE_URL=$(gcloud run services describe noshow-prediction-api \
  --region us-central1 \
  --format 'value(status.url)')

curl $SERVICE_URL/health
```

### View Logs
```bash
gcloud run services logs read noshow-prediction-api \
  --region us-central1 \
  --limit 50
```

### Monitor Metrics (Cloud Console)
```
https://console.cloud.google.com/run/detail/us-central1/noshow-prediction-api
```

---

## 🎯 Key Features

### ✅ Zero-Downtime Model Updates
- **Dynamic Loading**: Service automatically loads latest Production model
- **No Redeployment Required**: Model promotion doesn't require container rebuild
- **Reload Endpoint**: `/reload-model` triggers immediate model refresh

### ✅ CI/CD Pipeline
1. **Push to main** → Triggers deployment
2. **Build Docker image** → Push to Artifact Registry
3. **Deploy to Cloud Run** → Service updated automatically
4. **Health check** → Verify deployment success

### ✅ Model Lifecycle
1. Train multiple models (baseline → improved → best)
2. Register in MLflow with metrics
3. Promote best model to "Production" stage
4. Trigger model reload (manual or automated)
5. Service serves new model immediately

---

## 🔍 Troubleshooting

### Issue: Authentication Failed
```bash
# Re-authenticate
gcloud auth login
gcloud auth application-default login
```

### Issue: Permission Denied
```bash
# Verify service account permissions
gcloud projects get-iam-policy $PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:serviceAccount:$SERVICE_ACCOUNT_NAME@$PROJECT_ID.iam.gserviceaccount.com"
```

### Issue: Model Not Loading
```bash
# Check Cloud Run logs
gcloud run services logs read noshow-prediction-api --region us-central1

# Common causes:
# - MLflow tracking URI not configured
# - No model in Production stage
# - Model name mismatch
```

### Issue: Container Fails to Start
```bash
# Test locally first
docker run -p 8080:8080 noshow-predictor:local

# Check Dockerfile COPY paths
# Verify requirements.txt has all dependencies
```

---

## 🧪 Testing Production Endpoint

### Example Prediction Request
```bash
SERVICE_URL="https://noshow-prediction-api-xxx.a.run.app"

curl -X POST "$SERVICE_URL/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": 67890,
    "gender": "M",
    "age": 62,
    "scheduled_day": "2025-12-27T09:30:00",
    "appointment_day": "2026-01-10T11:00:00",
    "neighbourhood": "Central",
    "scholarship": true,
    "hypertension": true,
    "diabetes": true,
    "alcoholism": false,
    "handicap": 1,
    "sms_received": true
  }'
```

### Expected Response
```json
{
  "probability": 0.73,
  "is_no_show": true,
  "model_name": "noshow-prediction-model",
  "model_version": "3",
  "prediction_timestamp": "2025-12-27T18:45:32.123456"
}
```

---

## 📚 Additional Resources

- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Artifact Registry Guide](https://cloud.google.com/artifact-registry/docs)
- [GitHub Actions for GCP](https://github.com/google-github-actions)
- [MLflow Model Registry](https://mlflow.org/docs/latest/model-registry.html)

---

## 🎓 Academic Demonstration Value

This setup demonstrates:

1. **Containerization**: Docker multi-stage builds for production
2. **Cloud Deployment**: Serverless deployment with Cloud Run
3. **CI/CD Automation**: GitHub Actions for continuous deployment
4. **Model Registry**: MLflow integration for model versioning
5. **Dynamic Model Loading**: Zero-downtime model updates
6. **Monitoring**: Health checks and logging
7. **Security**: Service accounts with least privilege

---

## 💡 Cost Optimization

- **Free Tier**: Cloud Run offers 2 million requests/month free
- **Auto-scaling**: Scales to zero when not in use
- **Memory**: Adjust `--memory` flag based on model size
- **CPU**: Use `--cpu 1` for cost savings if latency is acceptable

---

## ✅ Verification Checklist

- [ ] GCP APIs enabled
- [ ] Artifact Registry created
- [ ] Service accounts created with correct permissions
- [ ] GitHub secrets configured
- [ ] Local Docker build successful
- [ ] GitHub Actions workflow runs without errors
- [ ] Cloud Run service accessible via HTTPS
- [ ] Health endpoint returns 200
- [ ] Prediction endpoint accepts requests
- [ ] Model reload endpoint works

---

**🎉 You're now ready to deploy your MLOps pipeline to production!**
