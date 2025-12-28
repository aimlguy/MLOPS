# Production Deployment Guide

## 🚀 Deployment Overview

### Architecture
- **Frontend**: Vercel (Static React App)
- **Backend**: Google Cloud Run (Node.js + Python)
- **Database**: Local SQLite (for demo) or upgrade to Cloud SQL PostgreSQL
- **CI/CD**: GitHub Actions

---

## 📋 Prerequisites

### 1. GitHub Setup
- Repository: `https://github.com/discount-Pieter-Levels/MLops.git`
- Create Personal Access Token (PAT):
  1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
  2. Generate new token with scopes: `repo`, `workflow`
  3. Save the token securely

### 2. Google Cloud Platform Setup
```bash
# Install Google Cloud SDK
# https://cloud.google.com/sdk/docs/install

# Login
gcloud auth login

# Create project (or use existing)
gcloud projects create mlops-production --name="MLOps Production"
gcloud config set project mlops-production

# Enable required APIs
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  containerregistry.googleapis.com \
  secretmanager.googleapis.com
```

### 3. Vercel Setup
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login
```

---

## 🔧 Step-by-Step Deployment

### Step 1: Configure Environment Variables

#### Create `.env.production` file:
```bash
# GitHub
GITHUB_TOKEN=your_github_pat_here
GITHUB_REPOSITORY=discount-Pieter-Levels/MLops

# Database (if upgrading from SQLite)
# DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Node
NODE_ENV=production
PORT=8080
```

#### Add secrets to Google Cloud:
```bash
# Add GitHub token to Secret Manager
echo -n "your_github_pat" | gcloud secrets create github-token --data-file=-

# Grant Cloud Run access
gcloud secrets add-iam-policy-binding github-token \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### Step 2: Train Models Locally
```bash
# Ensure models are trained before deployment
python src/train_models.py

# Verify models exist
ls models/
# Should see: xgboost.pkl, best_model_info.json, scaler.pkl, etc.
```

### Step 3: Deploy Backend to Google Cloud Run

```bash
# Build and deploy using Cloud Build
gcloud builds submit --config cloudbuild.yaml

# Or deploy directly
gcloud run deploy mlops-backend \
  --source . \
  --region us-central1 \
  --platform managed \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --set-env-vars NODE_ENV=production \
  --set-secrets GITHUB_TOKEN=github-token:latest

# Get the service URL
gcloud run services describe mlops-backend --region us-central1 --format='value(status.url)'
# Example output: https://mlops-backend-abc123-uc.a.run.app
```

### Step 4: Deploy Frontend to Vercel

```bash
# Update vercel.json with backend URL
# Replace "https://your-backend-url.run.app" with actual Cloud Run URL

# Deploy to Vercel
cd /path/to/MLops
vercel --prod

# Vercel will output: https://mlops-xxx.vercel.app
```

### Step 5: Configure GitHub Actions

#### Add repository secrets:
1. Go to GitHub repo → Settings → Secrets and variables → Actions
2. Add secrets:
   - `GITHUB_TOKEN`: Your PAT (for triggering workflows)
   - `GCP_PROJECT_ID`: Your GCP project ID
   - `GCP_SA_KEY`: Service account JSON key (for deployment)

#### Create GCP Service Account:
```bash
# Create service account
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions"

# Grant permissions
gcloud projects add-iam-policy-binding mlops-production \
  --member="serviceAccount:github-actions@mlops-production.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding mlops-production \
  --member="serviceAccount:github-actions@mlops-production.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Create and download key
gcloud iam service-accounts keys create github-actions-key.json \
  --iam-account=github-actions@mlops-production.iam.gserviceaccount.com

# Copy contents to GitHub secret GCP_SA_KEY
cat github-actions-key.json
```

---

## 🧪 Testing Production Deployment

### Test Backend
```bash
BACKEND_URL="https://mlops-backend-abc123-uc.a.run.app"

# Test health
curl $BACKEND_URL/api/pipeline/runs

# Test prediction
curl -X POST $BACKEND_URL/api/predict \
  -H "Content-Type: application/json" \
  -d '{
    "gender": "F",
    "age": 35,
    "neighbourhood": "JARDIM CAMBURI",
    "scholarship": false,
    "hypertension": false,
    "diabetes": false,
    "alcoholism": false,
    "handicap": 0,
    "smsReceived": true,
    "scheduledDay": "2024-04-01T10:00:00",
    "appointmentDay": "2024-04-15T14:00:00"
  }'

# Test monitoring
curl $BACKEND_URL/api/monitoring/status

# Trigger pipeline (requires GITHUB_TOKEN)
curl -X POST $BACKEND_URL/api/pipeline/trigger
```

### Test Frontend
Visit: `https://mlops-xxx.vercel.app`
- Navigate to Predictor page
- Make a prediction
- Check Monitoring page
- Trigger pipeline on Dashboard

---

## 📊 Monitoring Production

### Cloud Run Logs
```bash
# View logs
gcloud run services logs read mlops-backend \
  --region us-central1 \
  --limit 50

# Tail logs
gcloud run services logs tail mlops-backend \
  --region us-central1
```

### Metrics
```bash
# View metrics in Cloud Console
https://console.cloud.google.com/run/detail/us-central1/mlops-backend/metrics
```

### Prometheus Metrics Endpoint
```bash
curl $BACKEND_URL/metrics
```

---

## 🔄 CI/CD Pipeline

### Workflow Triggers

1. **Model Training** (`.github/workflows/model-training.yml`):
   - Triggered via API from frontend
   - Trains all models
   - Uploads artifacts

2. **CI** (`.github/workflows/ci.yml`):
   - Runs on PR
   - Linting, type-checking
   - Unit tests

3. **Deployment** (`.github/workflows/deploy-gcp.yml`):
   - Triggered on push to `main`
   - Builds Docker image
   - Deploys to Cloud Run

---

## 🔐 Security Checklist

- [ ] GitHub PAT stored in GitHub Secrets
- [ ] GCP Service Account key stored in GitHub Secrets  
- [ ] Cloud Run service requires authentication (or use API keys)
- [ ] Database credentials in Secret Manager
- [ ] CORS configured for Vercel domain only
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints

---

## 💰 Cost Estimation

### Google Cloud Run (Backend)
- **Free tier**: 2 million requests/month
- **After free tier**: ~$0.40 per million requests
- **Expected monthly**: $5-20 (low traffic)

### Vercel (Frontend)
- **Hobby plan**: Free
- **Pro plan**: $20/month (recommended for production)

### Total Estimated Cost: **$0-40/month**

---

## 🚨 Troubleshooting

### Issue: "Model not found"
```bash
# Ensure models are included in Docker build
docker build -f Dockerfile.production -t test .
docker run -it test ls -la models/
```

### Issue: "GitHub Actions not triggering"
- Verify GITHUB_TOKEN is set in backend
- Check token has `workflow` scope
- Verify workflow file name matches API call

### Issue: "CORS errors"
- Update CORS origins in `server/index.ts`
- Add Vercel domain to allowed origins

### Issue: "Out of memory"
- Increase Cloud Run memory: `--memory 4Gi`
- Optimize model loading (lazy load)

---

## 📝 Post-Deployment Tasks

1. **Update DNS** (optional):
   - Point custom domain to Vercel
   - Point API subdomain to Cloud Run

2. **Set up monitoring**:
   - Enable Cloud Monitoring alerts
   - Set up Sentry for error tracking

3. **Database migration** (if needed):
   - Migrate from SQLite to Cloud SQL PostgreSQL
   - Update connection string

4. **Documentation**:
   - Update README with production URLs
   - Document API endpoints

---

## 🎉 You're Live!

Your MLOps application is now production-ready and accessible worldwide:
- **Frontend**: https://mlops-xxx.vercel.app
- **Backend**: https://mlops-backend-xxx.run.app
- **Pipeline**: Triggered via GitHub Actions

Share the Vercel URL with anyone to access your application!
