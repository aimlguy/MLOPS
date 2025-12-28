# 🚀 Deploy to Production - Quick Guide

## What Just Happened?

✅ **Fixed Dockerfile**: Now copies `mlruns/` directory with your models  
✅ **Fixed .dockerignore**: No longer excludes mlruns  
✅ **Ready to Deploy**: Best model (v4, AUC 0.9347) will be in production

---

## Deploy Now (2 Options)

### Option A: Automatic CI/CD (Easiest) ⭐

```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "feat: deploy production model v4 (AUC 93.47%)"

# Push to trigger automatic deployment
git push origin main
```

**What happens next:**
1. GitHub Actions detects push
2. Runs `.github/workflows/deploy-gcp.yml`
3. Builds Docker image with mlruns/
4. Pushes to Google Artifact Registry
5. Updates Cloud Run service
6. **New model is live!** 🎉

**Monitor progress:**
- Go to GitHub → Actions tab
- Watch the deployment workflow
- Takes ~5-10 minutes

---

### Option B: Manual Deploy (Faster) ⚡

If GitHub Actions isn't working or you want immediate deployment:

```powershell
# 1. Authenticate with GCP
gcloud auth login
gcloud config set project ethika-rag-model

# 2. Build and submit to Cloud Build
gcloud builds submit --tag asia-south1-docker.pkg.dev/ethika-rag-model/noshow/predictor:v4 .

# 3. Deploy to Cloud Run
gcloud run deploy ethika-rag-model `
  --image asia-south1-docker.pkg.dev/ethika-rag-model/noshow/predictor:v4 `
  --platform managed `
  --region asia-south1 `
  --allow-unauthenticated `
  --set-env-vars MLFLOW_TRACKING_URI=file:///app/mlruns,MODEL_NAME=noshow-prediction-model
```

**Time:** ~3-5 minutes

---

## Verify Deployment

After deployment completes:

### 1. Check Health
```bash
curl https://ethika-rag-model-583756314894.asia-south1.run.app/health
```
Expected: `{"status":"healthy","timestamp":"..."}`

### 2. Check Model Version
```bash
curl https://ethika-rag-model-583756314894.asia-south1.run.app/model-info
```
Expected:
```json
{
  "name": "noshow-prediction-model",
  "version": "4",
  "stage": "Production",
  "loaded": true
}
```

### 3. Test Prediction
```bash
curl -X POST https://ethika-rag-model-583756314894.asia-south1.run.app/predict `
  -H "Content-Type: application/json" `
  -d '{
    "patient_id": 12345,
    "gender": "F",
    "age": 35,
    "scheduled_day": "2016-05-01T10:00:00",
    "appointment_day": "2016-05-05T10:00:00",
    "neighbourhood": "JARDIM CAMBURI",
    "scholarship": false,
    "hypertension": false,
    "diabetes": false,
    "alcoholism": false,
    "handicap": 0,
    "sms_received": true
  }'
```

Expected response with **high-quality predictions from v4 model**!

---

## Before vs After Deployment

### Before 🔴
```
┌─────────────────────┐
│  Local (Your PC)    │
│  Model v4: AUC 0.93 │  ✅ Best model trained
└─────────────────────┘

┌─────────────────────┐
│  Cloud Run          │
│  Model: Unknown/Old │  ❌ No model or old version
└─────────────────────┘
```

### After ✅
```
┌─────────────────────┐
│  Local (Your PC)    │
│  Model v4: AUC 0.93 │  ✅ Best model trained
└─────────────────────┘
           │
           │ git push
           ▼
┌─────────────────────┐
│  Cloud Run          │
│  Model v4: AUC 0.93 │  ✅ Production serving best model!
└─────────────────────┘
```

---

## Why This Matters for Your Project 🎓

This completes the **full MLOps cycle**:

1. ✅ Train models locally (DONE)
2. ✅ Track experiments in MLflow (DONE)
3. ✅ Automatic model promotion (DONE)
4. ✅ **Deploy to production** (ABOUT TO DO)
5. ✅ Serve predictions via API (WILL BE ACTIVE)

**For grading/demo:**
- Show the progression: baseline → improved → best
- Demonstrate automatic promotion (v3 was rejected)
- Show production API serving the best model
- Prove end-to-end automation

---

## Recommended: Deploy Now!

```bash
# Do this now
git add .
git commit -m "feat: deploy production model v4 (AUC 93.47%)"
git push origin main
```

Then show your instructor:
1. GitHub Actions deployment log
2. Cloud Run service with new model
3. API returning predictions from v4
4. MLflow registry showing version history

**This demonstrates a complete, production-ready MLOps pipeline!** 🚀
